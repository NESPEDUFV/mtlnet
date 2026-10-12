import os
from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd
from pandas import DataFrame


def get_parent_of_src(project_root: Path) -> Optional[Path]:
    """
    If `src` appears in `project_root` path (or any ancestor), return the parent directory of that `src`.
    Otherwise return None.
    """
    for p in (project_root, *project_root.parents):
        if p.name == "src":
            return p.parent
    return None

# Base directories
PROJECT_ROOT = get_parent_of_src(Path(__file__).parent.parent)
DATA_ROOT = Path(os.environ.get('DATA_ROOT', PROJECT_ROOT / 'data'))
OUTPUT_DIR = Path(os.environ.get('OUTPUT_DIR', PROJECT_ROOT / 'output'))
RESULTS_ROOT = Path(os.environ.get('RESULTS_ROOT', PROJECT_ROOT / 'results'))

# Input data paths
IO_CHECKINS = DATA_ROOT / 'checkins'


class EmbeddingEngine(Enum):
    DGI = "dgi"
    HGI = "hgi"
    HMRM = "hmrm"
    TIME2VEC = "time2vec"
    SPACE2VEC = "space2vec"
    SPHERE2VEC = "sphere2vec"
    CHECK2HGI = "check2hgi"
    CHECK2HGI_POOLED = "check2hgi_pooled"  # POI-mean-pooled C4 counterfactual
    CHECK2HGI_POI2VEC = "check2hgi_poi2vec"  # POI2Vec-augmented features (probe)
    C2HGI_HGI_CONCAT = "c2hgi_hgi_concat"  # Design A: late concat fusion (probe)
    CHECK2HGI_DESIGN_E = "check2hgi_design_e"  # Design E: POI2Vec input + stop-grad encoder (probe)
    CHECK2HGI_DESIGN_B = "check2hgi_design_b"  # Design B: POI2Vec at POI-pool boundary, cat path canonical (probe)
    CHECK2HGI_DESIGN_H = "check2hgi_design_h"  # Design H: learnable POI table at POI-pool boundary (probe)
    CHECK2HGI_DESIGN_D = "check2hgi_design_d"  # Design D: heterograph encoder (probe)
    CHECK2HGI_DESIGN_I = "check2hgi_design_i"  # Design I: LoRA-style low-rank correction (probe)
    CHECK2HGI_DESIGN_J = "check2hgi_design_j"  # Design J: H + anchor regularization (probe)
    CHECK2HGI_DESIGN_M = "check2hgi_design_m"  # Design M: B + POI-side distillation (probe)
    CHECK2HGI_DESIGN_L = "check2hgi_design_l"  # Design L (Lever 5): KL-distill on top-k neighbour softmax (probe)
    CHECK2HGI_LEVER4_CANONICAL = "check2hgi_lever4_canonical"  # Lever 4: canonical + p2r region-prior (Tier B B3 control)
    CHECK2HGI_LEVER4_DESIGN_B = "check2hgi_lever4_design_b"    # Lever 4: Design B + p2r region-prior (Tier B B3 winner-stack)
    CHECK2HGI_RESLN = "check2hgi_resln"  # tier_resln: ResidualLNEncoder substrate (canonical_improvement T3.2)
    CHECK2HGI_RESLN_DESIGN_B = "check2hgi_resln_design_b"  # tier_resln: ResLN encoder + Design B POI2Vec injection
    CHECK2HGI_RESLN_DESIGN_B_SIDEFEAT = "check2hgi_resln_design_b_sidefeat"  # v13 + T4.3 side-features (no-stack, eval-only; not adopted)
    CHECK2HGI_DESIGN_K_L0_1 = "check2hgi_design_k_l0_1"  # design_k: c2hgi + HGI Delaunay POI-GCN (reg path), λ=0.1 — closes 54-78% of HGI next-reg gap
    CHECK2HGI_MAE = "check2hgi_mae"  # T5.2b masked-POI feature-aggregate reconstruction (cat-axis lever; re-test at FL)
    CHECK2HGI_DESIGN_K_RESLN_L0_1 = "check2hgi_design_k_resln_l0_1"  # design_k + resln encoder (cat disentangle)
    CHECK2HGI_DESIGN_K_RESLN_MAE_L0_1 = "check2hgi_design_k_resln_mae_l0_1"  # design_k + resln + T5.2b mae (full dual-axis stack)
    CHECK2HGI_RESLN_DESIGN_J = "check2hgi_resln_design_j"  # tier_resln: ResLN encoder + Design J anchored learnable POI table
    # [2026-08-16] Q13, o braco de concatenacao. O place embedding com as features por visita
    # ja concatenadas no proprio next.parquet, 9 blocos de 75 em vez de 64. Existe como engine
    # separada para que o braco rode pelo caminho de treino normal, sem alterar train.py.
    HGI_OVL_FEAT = "hgi_ovl_feat"
    CHECK2HGI_DK_OVL = "check2hgi_dk_ovl"  # v14 (design_k) embeddings re-windowed at stride=1 (OVERLAPPING) — overlap-window real-pipeline probe; embeddings/region symlinked from v14, only the windowing differs
    # integrity_v2 consecutive-link study (2026-08-06). Same dk_ovl row space and region labels;
    # the ONLY difference is which edges existed when the check-in vectors were computed, so the
    # reported dedicated recipe runs on them unchanged and is comparable to the reported column.
    # STUDY engines: not for any headline dissertation number.
    CHECK2HGI_IV2_STRICT = "check2hgi_iv2_strict"
    CHECK2HGI_IV2_CAUSAL = "check2hgi_iv2_causal"
    CHECK2HGI_IV2_F25 = "check2hgi_iv2_f25"
    CHECK2HGI_IV2_F125 = "check2hgi_iv2_f125"
    CHECK2HGI_IV2_L4 = "check2hgi_iv2_l4"
    CHECK2HGI_IV2_L3 = "check2hgi_iv2_l3"
    CHECK2HGI_IV2_L1 = "check2hgi_iv2_l1"
    CHECK2HGI_IV2_F50 = "check2hgi_iv2_f50"
    CHECK2HGI_IV2_W128 = "check2hgi_iv2_w128"
    CHECK2HGI_IV2_W32 = "check2hgi_iv2_w32"
    CHECK2HGI_IV2_R2 = "check2hgi_iv2_r2"
    CHECK2HGI_IV2_R1 = "check2hgi_iv2_r1"
    CHECK2HGI_IV2_E5 = "check2hgi_iv2_e5"
    CHECK2HGI_IV2_E4 = "check2hgi_iv2_e4"
    CHECK2HGI_IV2_E3 = "check2hgi_iv2_e3"
    CHECK2HGI_IV2_E1 = "check2hgi_iv2_e1"
    CHECK2HGI_IV2_E2 = "check2hgi_iv2_e2"
    CHECK2HGI_IV2_E12 = "check2hgi_iv2_e12"
    CHECK2HGI_IV2_LABELONLY = "check2hgi_iv2_labelonly"
    CHECK2HGI_IV2_D1 = "check2hgi_iv2_d1"
    CHECK2HGI_IV2_B1 = "check2hgi_iv2_b1"
    # v18 (2026-08-06): the v17 recipe on a leak-free substrate — the consecutive-visit
    # graph is FORWARD-ONLY in training and at readout, plus 4 elapsed-time node columns
    # (in_channels 15 = canonical 11 + continuous_time 4). Same dk_ovl row space and region
    # labels as v17, so the frozen recipe runs on it unchanged and the columns are comparable.
    # Built by scripts/integrity_v2/build_study_repr.py --forward-only --add-continuous-time.
    CHECK2HGI_V18 = "check2hgi_v18"
    # embedding_eval re-screen variants (2026-06-01) — rebuilt via OUTPUT_DIR-scratch,
    # harvested to output/<value>/; do NOT overwrite the frozen output/check2hgi/.
    CHECK2HGI_GCN_CTRL = "check2hgi_gcn_ctrl"        # fresh GCN wd=0 control (same-protocol baseline for the re-screen)
    CHECK2HGI_V3C_WD05 = "check2hgi_v3c_wd05"        # T1.5 v3c: AdamW weight-decay 5e-2 (GCN base)
    CHECK2HGI_T24_DROPEDGE = "check2hgi_t24_dropedge"  # T2.4: symmetric DropEdge on user-seq edges
    CHECK2HGI_T43_SIDEFEAT = "check2hgi_t43_sidefeat"  # T4.3: POI side-features (no_covisit subset)
    CHECK2HGI_GAT = "check2hgi_gat"                   # T3.1: GATv2 encoder (leak-sniff)
    CHECK2HGI_RGCN = "check2hgi_rgcn"                 # T3.3: R-GCN relation-typed (leak-sniff)
    CHECK2HGI_T61_P2P = "check2hgi_t61_p2p"          # T6.1: POI-POI InfoNCE 4th boundary
    # re-screen candidates stacked on the ResLN encoder base (v13 encoder)
    CHECK2HGI_RESLN_V3C = "check2hgi_resln_v3c"
    CHECK2HGI_RESLN_DROPEDGE = "check2hgi_resln_dropedge"
    CHECK2HGI_RESLN_SIDEFEAT = "check2hgi_resln_sidefeat"
    CHECK2HGI_RESLN_P2P = "check2hgi_resln_p2p"
    CHECK2HGI_GPROP = "check2hgi_gprop"  # baseline check-in emb + GCN^2-propagated region emb (adjacency-aware head proxy)
    CHECK2HGI_RESLN_DESIGN_B_GPROP = "check2hgi_resln_design_b_gprop"  # v13 + GCN^2 region emb
    # ── external-baseline probe engines (scripts/baselines/) ──────────────────
    # [ENUM-MERGE] appended at the END; do NOT reorder existing members. Value-keyed
    # routing → inert for the champion (which uses check2hgi_design_k_resln_mae_l0_1).
    BASELINE_B2C_ONEHOT64 = "baseline_b2c_onehot64"  # B2c: FIXED 64-d seeded random projection of POI id (zero-training floor; NO pretrain → leak-trivial, windowing-independent, reusable)
    CHECK2HGI_CTLE = "check2hgi_ctle"  # B1: CTLE (Lin et al. AAAI'21) contextual per-visit embedding (MLM+MH pretrain, leak-safe per fold)
    BASELINE_B2A_POI2VEC = "baseline_b2a_poi2vec"  # B2a: faithful AAAI'17 POI2Vec (CBOW + midpoint tree + overlap-area phi + user term, leak-safe per fold)
    BASELINE_GEOTREE_SKIPGRAM = "baseline_geotree_skipgram"  # geo-tree-regularized skip-gram (the renamed, honest non-POI2Vec baseline)
    POI2HGI = "poi2hgi"
    FUSION = "fusion"  # Multi-embedding fusion
    # [ENUM-MERGE] Blocker 2 (Tbl 2, closing_data): HGI POI embeddings under the OVERLAP
    # windowing — the frozen check2hgi_dk_ovl stride-1/MIN_SEQ=10/gated sequences remapped
    # through the HGI POI lookup. Windows byte-identical to the Check2HGI arm; only the
    # embedding lookup differs (cat-STL substrate contrast on ONE windowing).
    HGI_DK_OVL = "hgi_dk_ovl"
    # v18-untrained floor arm (2026-09-06): architecture at initialization, no training step,
    # per-repr-seed probe for the check2hgi_integrity_v2 "how much is raw features vs graph
    # training" ablation. Never for any headline number. [ENUM-MERGE] appended at the END.
    CHECK2HGI_V18_UNTRAINED_S42 = "check2hgi_v18_untrained_s42"
    CHECK2HGI_V18_UNTRAINED_S0 = "check2hgi_v18_untrained_s0"
    CHECK2HGI_V18_UNTRAINED_S1 = "check2hgi_v18_untrained_s1"
    CHECK2HGI_V18_UNTRAINED_S7 = "check2hgi_v18_untrained_s7"
    # integrity re-run on the delivered protocol (2026-09-30): v18 representation rebuilt per fold
    # from TRAINING USERS ONLY (split = integrity_v2 freeze_split.py on check2hgi_dk_ovl, seed 0),
    # all users then encoded with those weights. One engine per fold, states as subdirs. Study
    # engines, never a headline number. [ENUM-MERGE] appended at the END.
    CHECK2HGI_V18_TO_F0 = "check2hgi_v18_to_f0"
    CHECK2HGI_V18_TO_F1 = "check2hgi_v18_to_f1"
    CHECK2HGI_V18_TO_F2 = "check2hgi_v18_to_f2"
    CHECK2HGI_V18_TO_F3 = "check2hgi_v18_to_f3"
    CHECK2HGI_V18_TO_F4 = "check2hgi_v18_to_f4"


# Engines valid for the MTL_CHECK2HGI (check-in-level joint) preset: check-in-level
# Check2HGI substrates + the per-visit baselines that share next.parquet/next_region.parquet.
# Single source of truth — the check2hgi-MTL fold creator (data/folds.py) and the train.py
# preset pre-flight BOTH validate against this, so a new engine is enabled in ONE place.
MTL_CHECK2HGI_ALLOWED_ENGINES = (
    EmbeddingEngine.CHECK2HGI,
    EmbeddingEngine.HGI,
    EmbeddingEngine.CHECK2HGI_DESIGN_B,
    EmbeddingEngine.CHECK2HGI_DESIGN_J,
    EmbeddingEngine.CHECK2HGI_DESIGN_L,
    EmbeddingEngine.CHECK2HGI_LEVER4_CANONICAL,
    EmbeddingEngine.CHECK2HGI_LEVER4_DESIGN_B,
    EmbeddingEngine.CHECK2HGI_RESLN,
    EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_B,
    EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_J,
    EmbeddingEngine.CHECK2HGI_T43_SIDEFEAT,  # embedding_eval MTL re-screen
    EmbeddingEngine.CHECK2HGI_GPROP,         # GCN^2 region-emb proxy
    EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_B_GPROP,  # v13 + GCN^2 region
    EmbeddingEngine.CHECK2HGI_DESIGN_K_L0_1,
    EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_L0_1,
    EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_MAE_L0_1,  # option-b dual-axis base
    EmbeddingEngine.CHECK2HGI_DK_OVL,  # overlap-window probe (v14 re-windowed stride=1)
    EmbeddingEngine.CHECK2HGI_IV2_STRICT,  # integrity_v2: target withheld at readout
    EmbeddingEngine.CHECK2HGI_IV2_CAUSAL,  # integrity_v2: forward-only trained and read
    EmbeddingEngine.CHECK2HGI_IV2_F25,
    EmbeddingEngine.CHECK2HGI_IV2_F125,
    EmbeddingEngine.CHECK2HGI_IV2_L4,
    EmbeddingEngine.CHECK2HGI_IV2_L3,
    EmbeddingEngine.CHECK2HGI_IV2_L1,
    EmbeddingEngine.CHECK2HGI_IV2_F50,
    EmbeddingEngine.CHECK2HGI_IV2_W128,
    EmbeddingEngine.CHECK2HGI_IV2_W32,
    EmbeddingEngine.CHECK2HGI_IV2_R2,
    EmbeddingEngine.CHECK2HGI_IV2_R1,
    EmbeddingEngine.CHECK2HGI_IV2_E5,
    EmbeddingEngine.CHECK2HGI_IV2_E4,
    EmbeddingEngine.CHECK2HGI_IV2_E3,
    EmbeddingEngine.CHECK2HGI_IV2_E1,
    EmbeddingEngine.CHECK2HGI_IV2_E2,
    EmbeddingEngine.CHECK2HGI_IV2_E12,
    EmbeddingEngine.CHECK2HGI_IV2_LABELONLY,
    EmbeddingEngine.CHECK2HGI_IV2_D1,
    EmbeddingEngine.CHECK2HGI_IV2_B1,
    EmbeddingEngine.CHECK2HGI_V18,  # v18: forward-only graph + elapsed-time node features
    EmbeddingEngine.BASELINE_B2C_ONEHOT64,  # [ENUM-MERGE] B2c zero-training floor probe
    EmbeddingEngine.CHECK2HGI_CTLE,  # [ENUM-MERGE] B1 CTLE contextual per-visit substrate
    EmbeddingEngine.BASELINE_B2A_POI2VEC,  # [ENUM-MERGE] B2a faithful POI2Vec
    EmbeddingEngine.BASELINE_GEOTREE_SKIPGRAM,  # [ENUM-MERGE] geo-tree skip-gram baseline
)


class Resources:
    """
    Static paths for resource files.
    """
    _miscellaneous_dir = DATA_ROOT / "miscellaneous"
    _gowalla_dir = DATA_ROOT / "gowalla"
    # US Census TIGER tract shapefiles (Gowalla states)
    TL_AL: Path = _miscellaneous_dir / "tl_2022_01_tract_AL" / "tl_2022_01_tract.shp"
    TL_AZ: Path = _miscellaneous_dir / "tl_2022_04_tract_AZ" / "tl_2022_04_tract.shp"
    TL_GA: Path = _miscellaneous_dir / "tl_2022_13_tract_GA" / "tl_2022_13_tract.shp"
    TL_FL: Path = _miscellaneous_dir / "tl_2022_12_tract_FL" / "tl_2022_12_tract.shp"
    TL_CA: Path = _miscellaneous_dir / "tl_2022_06_tract_CA" / "tl_2022_06_tract.shp"
    TL_TX: Path = _miscellaneous_dir / "tl_2022_48_tract_TX" / "tl_2022_48_tract.shp"
    # New York state tracts — covers NYC (FSQ + STEPS).
    # Download: https://www2.census.gov/geo/tiger/TIGER2022/TRACT/tl_2022_36_tract.zip
    TL_NY: Path = _miscellaneous_dir / "tl_2022_36_tract_NY" / "tl_2022_36_tract.shp"
    # Sentinel for grid-based synthetic boroughs (international cities: Tokyo, etc.)
    # When set to None in the HGI pipeline, grid_boroughs.create_grid_boroughs() is used.
    GRID: None = None

    # ── Gowalla raw inputs (consumed by src/etl/gowalla/) ──────────────────
    # See pipelines/etl/gowalla.pipe.py for a turnkey wrapper.
    CHECKINS_PARQUET: Path = _gowalla_dir / "gowalla_checkins.parquet"
    CHECKINS: Path = _gowalla_dir / "gowalla_checkins.csv"
    SPOTS: Path = _gowalla_dir / "gowalla_spots_subset1.csv"
    SPOTS_2: Path = _gowalla_dir / "gowalla_spots_subset2.csv"
    CATEGORIES_STRUCTURE: Path = _gowalla_dir / "gowalla_category_structure.json"
    CATEGORIES_CALLBACK: Path = _gowalla_dir / "callback_categories.json"
    EXTRA_CATEGORIES_CALLBACK: Path = _gowalla_dir / "extra_categories.json"
    # US states shapefile — download from Census TIGER:
    # https://www2.census.gov/geo/tiger/TIGER2022/STATE/tl_2022_us_state.zip
    STATES_US: Path = _miscellaneous_dir / "tl_2022_us_state" / "tl_2022_us_state.shp"
    # Timezone polygons — used by stage 2 to compute local_datetime per checkin.
    # Download from https://github.com/evansiroky/timezone-boundary-builder/releases
    # (combined-shapefile-with-oceans variant).
    TIMEZONES: Path = _miscellaneous_dir / "combined-shapefile-with-oceans" / "combined-shapefile-with-oceans.shp"



class _DGIIoPath:
    # File name constants
    CTA_FILE: str = "cta.csv"
    INTER_DATA_FILE: str = "data_inter.pkl"

    # DGI embeddings output
    _dgi_dir: Path = OUTPUT_DIR / EmbeddingEngine.DGI.value

    @classmethod
    def get_state_dir(cls, state: str) -> Path:
        """Get the DGI output directory for a specific state."""
        return cls._dgi_dir / state.lower()

    @classmethod
    def get_output_dir(cls, state: str) -> Path:
        return cls.get_state_dir(state)

    @classmethod
    def get_temp_dir(cls, state: str) -> Path:
        """Get the temp directory for a specific state."""
        return cls.get_output_dir(state) / "temp"

    @classmethod
    def get_inter_file(cls, state: str) -> Path:
        """Get the intermediate data file path for a specific state."""
        return cls.get_temp_dir(state) / cls.INTER_DATA_FILE

    @classmethod
    def get_cta_file(cls, state: str) -> Path:
        """Get the CTA file path for a specific state."""
        return cls.get_temp_dir(state) / cls.CTA_FILE


class _HGIIoPath:
    # File name constants
    POIS_FILE: str = "pois_gowalla.csv"
    BOROUGHS_FILE: str = "boroughs_area.csv"
    POI_EMB_FILE: str = "poi-encoder.tensor"
    GRAPH_DATA_FILE: str = "gowalla.pt"
    POI_INDEX_FILE: str = "poi_index.csv"
    POI_REGION_MAP_FILE: str = "poi_region_map.csv"
    EDGES_FILE: str = "edges.csv"
    POIS_PROCESSED_FILE: str = "pois.csv"

    # HGI embeddings output
    _hgi_dir: Path = OUTPUT_DIR / EmbeddingEngine.HGI.value

    @classmethod
    def get_state_dir(cls, state: str) -> Path:
        """Get the HGI output directory for a specific state."""
        return cls._hgi_dir / state.lower()

    @classmethod
    def get_output_dir(cls, state: str) -> Path:
        return cls.get_state_dir(state)

    @classmethod
    def get_temp_dir(cls, state: str) -> Path:
        """Get the temp directory for a specific state."""
        return cls.get_output_dir(state) / "temp"

    @classmethod
    def get_pois_file(cls, state: str) -> Path:
        """Get the POIs file path for a specific state."""
        return cls.get_temp_dir(state) / cls.POIS_FILE

    @classmethod
    def get_boroughs_file(cls, state: str) -> Path:
        """Get the boroughs file path for a specific state."""
        return cls.get_temp_dir(state) / cls.BOROUGHS_FILE

    @classmethod
    def get_poi_emb_file(cls, state: str) -> Path:
        """Get the POI embeddings file path for a specific state."""
        return cls.get_temp_dir(state) / cls.POI_EMB_FILE

    @classmethod
    def get_graph_data_file(cls, state: str) -> Path:
        """Get the graph data file path for a specific state."""
        return cls.get_temp_dir(state) / cls.GRAPH_DATA_FILE

    @classmethod
    def get_poi_index_file(cls, state: str) -> Path:
        """Get the POI index file path for a specific state."""
        return cls.get_temp_dir(state) / cls.POI_INDEX_FILE

    @classmethod
    def get_poi_region_map_file(cls, state: str) -> Path:
        """Get the POI region map file path for a specific state."""
        return cls.get_temp_dir(state) / cls.POI_REGION_MAP_FILE

    @classmethod
    def get_edges_file(cls, state: str) -> Path:
        """Get the edges file path for a specific state."""
        return cls.get_temp_dir(state) / cls.EDGES_FILE

    @classmethod
    def get_pois_processed_file(cls, state: str) -> Path:
        """Get the processed POIs file path for a specific state."""
        return cls.get_temp_dir(state) / cls.POIS_PROCESSED_FILE


class _Time2VecIoPath:
    # File name constants
    MODEL_FILE: str = "time2vec_model.pt"

    # Time2Vec embeddings output
    _time2vec_dir: Path = OUTPUT_DIR / EmbeddingEngine.TIME2VEC.value

    @classmethod
    def get_state_dir(cls, state: str) -> Path:
        """Get the Time2Vec output directory for a specific state."""
        return cls._time2vec_dir / state.lower()

    @classmethod
    def get_output_dir(cls, state: str) -> Path:
        return cls.get_state_dir(state)

    @classmethod
    def get_model_file(cls, state: str) -> Path:
        """Get the trained model file path for a specific state."""
        return cls.get_output_dir(state) / cls.MODEL_FILE


class _Space2VecIoPath:
    # File name constants
    MODEL_FILE: str = "space2vec_model.pt"
    PAIRS_I_FILE: str = "pairs_i.int32"
    PAIRS_J_FILE: str = "pairs_j.int32"
    PAIRS_Y_FILE: str = "pairs_y.uint8"
    PAIRS_COUNT_FILE: str = "pairs_count.npy"

    # Space2Vec embeddings output
    _space2vec_dir: Path = OUTPUT_DIR / EmbeddingEngine.SPACE2VEC.value

    @classmethod
    def get_state_dir(cls, state: str) -> Path:
        """Get the Space2Vec output directory for a specific state."""
        return cls._space2vec_dir / state.lower()

    @classmethod
    def get_output_dir(cls, state: str) -> Path:
        return cls.get_state_dir(state)

    @classmethod
    def get_temp_dir(cls, state: str) -> Path:
        """Get the temp directory for memmap pair files."""
        return cls.get_output_dir(state) / "temp"

    @classmethod
    def get_model_file(cls, state: str) -> Path:
        """Get the trained model file path for a specific state."""
        return cls.get_output_dir(state) / cls.MODEL_FILE

    @classmethod
    def get_pairs_dir(cls, state: str) -> Path:
        """Get the directory for memmap pair files."""
        return cls.get_temp_dir(state)


class _Sphere2VecIoPath:
    # File name constants
    MODEL_FILE: str = "sphere2vec_model.pt"

    # Sphere2Vec embeddings output
    _sphere2vec_dir: Path = OUTPUT_DIR / EmbeddingEngine.SPHERE2VEC.value

    @classmethod
    def get_state_dir(cls, state: str) -> Path:
        """Get the Sphere2Vec output directory for a specific state."""
        return cls._sphere2vec_dir / state.lower()

    @classmethod
    def get_output_dir(cls, state: str) -> Path:
        return cls.get_state_dir(state)

    @classmethod
    def get_model_file(cls, state: str) -> Path:
        """Get the trained model file path for a specific state."""
        return cls.get_output_dir(state) / cls.MODEL_FILE


class _Check2HGIIoPath:
    # File name constants
    GRAPH_DATA_FILE: str = "checkin_graph.pt"
    BOROUGHS_FILE: str = "boroughs_area.csv"

    # Check2HGI embeddings output
    _check2hgi_dir: Path = OUTPUT_DIR / EmbeddingEngine.CHECK2HGI.value

    @classmethod
    def get_state_dir(cls, state: str) -> Path:
        """Get the Check2HGI output directory for a specific state."""
        return cls._check2hgi_dir / state.lower()

    @classmethod
    def get_output_dir(cls, state: str) -> Path:
        return cls.get_state_dir(state)

    @classmethod
    def get_temp_dir(cls, state: str) -> Path:
        """Get the temp directory for a specific state."""
        return cls.get_output_dir(state) / "temp"

    @classmethod
    def get_graph_data_file(cls, state: str) -> Path:
        """Get the graph data file path for a specific state."""
        return cls.get_temp_dir(state) / cls.GRAPH_DATA_FILE

    @classmethod
    def get_boroughs_file(cls, state: str) -> Path:
        """Get the boroughs file path for a specific state."""
        return cls.get_temp_dir(state) / cls.BOROUGHS_FILE


class _POI2HGIIoPath:
    # File name constants
    GRAPH_DATA_FILE: str = "poi_graph.pt"
    BOROUGHS_FILE: str = "boroughs_area.csv"

    # POI2HGI embeddings output
    _poi2hgi_dir: Path = OUTPUT_DIR / EmbeddingEngine.POI2HGI.value

    @classmethod
    def get_state_dir(cls, state: str) -> Path:
        """Get the POI2HGI output directory for a specific state."""
        return cls._poi2hgi_dir / state.lower()

    @classmethod
    def get_output_dir(cls, state: str) -> Path:
        return cls.get_state_dir(state)

    @classmethod
    def get_temp_dir(cls, state: str) -> Path:
        """Get the temp directory for a specific state."""
        return cls.get_output_dir(state) / "temp"

    @classmethod
    def get_graph_data_file(cls, state: str) -> Path:
        """Get the graph data file path for a specific state."""
        return cls.get_temp_dir(state) / cls.GRAPH_DATA_FILE

    @classmethod
    def get_boroughs_file(cls, state: str) -> Path:
        """Get the boroughs file path for a specific state."""
        return cls.get_temp_dir(state) / cls.BOROUGHS_FILE


class IoPaths:
    """
    Static paths for I/O operations.
    """
    EMBEDDINGS_FILE: str = "embeddings.parquet"

    # ── Gowalla ETL artefacts (raw → labelled → localised → per-state) ─────
    _gowalla_etl_dir: Path = DATA_ROOT / "temp" / "gowalla"
    CHECKINS_ETL_STEP_1: Path = _gowalla_etl_dir / "stage1_categorised.parquet"
    CHECKINS_ETL_STEP_2: Path = _gowalla_etl_dir / "stage2_localised.parquet"
    CHECKINS_ETL_STEP_3: Path = _gowalla_etl_dir / "stage3_states.parquet"
    CHECKINS_ETL_STEP_3_CSV: Path = _gowalla_etl_dir / "stage3_states.csv"
    CHECKINS_ETL_STATES: Path = DATA_ROOT / "checkins"
    CHECKINS_ETL_STATES_PARQUET: Path = DATA_ROOT / "checkins_parquet"

    @classmethod
    def validate(cls) -> None:
        """Check that required data directories exist and create output directories.

        Call this at pipeline startup, not at import time.
        Raises FileNotFoundError if checkins directory is missing.
        """
        if not IO_CHECKINS.exists() or not IO_CHECKINS.is_symlink():
            raise FileNotFoundError(f"Checkins directory not found: {IO_CHECKINS}")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_ROOT.mkdir(parents=True, exist_ok=True)

    DGI = _DGIIoPath
    HGI = _HGIIoPath
    TIME2VEC = _Time2VecIoPath
    SPACE2VEC = _Space2VecIoPath
    SPHERE2VEC = _Sphere2VecIoPath
    CHECK2HGI = _Check2HGIIoPath
    POI2HGI = _POI2HGIIoPath


    @classmethod
    def get_embedd(cls, state: str, embedd_engine: EmbeddingEngine) -> Path:
        """Get the embeddings file for a specific state and engine."""
        if embedd_engine == EmbeddingEngine.FUSION:
            raise ValueError(
                "FUSION is a synthetic engine (task-specific). "
                "Use get_fusion_category() or get_fusion_next() instead."
            )
        return OUTPUT_DIR / embedd_engine.value / state.lower() / cls.EMBEDDINGS_FILE

    @classmethod
    def load_embedd(cls, state: str, embedd_engine: EmbeddingEngine) -> DataFrame:
        """Load embeddings for a specific state and embedding engine."""
        return pd.read_parquet(cls.get_embedd(state, embedd_engine))

    @classmethod
    def get_city(cls, state: str, ext: str = 'parquet') -> Path:
        return DATA_ROOT / 'checkins' / f"{state.capitalize()}.{ext}"

    @classmethod
    def load_city(cls, state: str, ext: str = 'parquet') -> DataFrame:
        """Load check-in data for a specific state."""
        return pd.read_parquet(cls.get_city(state, ext))

    @classmethod
    def get_input_dir(cls, state: str, embedd_engine: EmbeddingEngine) -> Path:
        return OUTPUT_DIR / embedd_engine.value / state.lower() / "input"

    @classmethod
    def get_category(cls, state: str, embedd_engine: EmbeddingEngine):
        """Get category input path (routes FUSION automatically)."""
        if embedd_engine == EmbeddingEngine.FUSION:
            return cls.get_fusion_category(state)
        return cls.get_input_dir(state, embedd_engine) / "category.parquet"

    @classmethod
    def load_category(cls, state: str, embedd_engine: EmbeddingEngine) -> DataFrame:
        """Load category input data for a specific state and engine."""
        return pd.read_parquet(cls.get_category(state, embedd_engine))

    @classmethod
    def get_next(cls, state: str, embedd_engine: EmbeddingEngine):
        """Get next-POI input path (routes FUSION automatically)."""
        if embedd_engine == EmbeddingEngine.FUSION:
            return cls.get_fusion_next(state)
        return cls.get_input_dir(state, embedd_engine) / "next.parquet"

    @classmethod
    def get_next_region(cls, state: str, embedd_engine: EmbeddingEngine) -> Path:
        """Next-region input path.

        The next-region *label space* is derived from the check2HGI
        preprocessing graph artifact (``poi_to_region`` tensor) — that
        labelling is substrate-independent. Each engine that wants to
        run a region task must publish its own ``input/next_region.parquet``
        with substrate-specific embedding columns (built by
        ``scripts/probe/build_hgi_next_region.py`` and friends).

        Currently supported: CHECK2HGI (canonical), HGI (built for the
        Phase-1 MTL counterfactual; see SUBSTRATE_COMPARISON_PLAN §5).
        Other engines: port the builder + pre-stage the parquet first.
        """
        supported = (
            EmbeddingEngine.CHECK2HGI,
            EmbeddingEngine.HGI,
            EmbeddingEngine.CHECK2HGI_POI2VEC,
            EmbeddingEngine.C2HGI_HGI_CONCAT,
            EmbeddingEngine.CHECK2HGI_DESIGN_E,
            EmbeddingEngine.CHECK2HGI_DESIGN_B,
            EmbeddingEngine.CHECK2HGI_DESIGN_H,
            EmbeddingEngine.CHECK2HGI_DESIGN_D,
            EmbeddingEngine.CHECK2HGI_DESIGN_I,
            EmbeddingEngine.CHECK2HGI_DESIGN_J,
            EmbeddingEngine.CHECK2HGI_DESIGN_M,
            EmbeddingEngine.CHECK2HGI_DESIGN_L,
            EmbeddingEngine.CHECK2HGI_LEVER4_CANONICAL,
            EmbeddingEngine.CHECK2HGI_LEVER4_DESIGN_B,
            EmbeddingEngine.CHECK2HGI_RESLN,
            EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_B,
            EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_J,
            EmbeddingEngine.CHECK2HGI_T43_SIDEFEAT,  # embedding_eval MTL re-screen
            EmbeddingEngine.CHECK2HGI_GPROP,         # GCN^2 region-emb proxy
            EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_B_GPROP,  # v13 + GCN^2 region
            EmbeddingEngine.CHECK2HGI_DESIGN_K_L0_1,          # design_k (Delaunay reg lever)
            EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_L0_1,    # design_k + resln
            EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_MAE_L0_1,  # dual-axis champion (option-b base)
            EmbeddingEngine.CHECK2HGI_DK_OVL,  # overlap-window real-pipeline probe (v14 re-windowed stride=1)
            EmbeddingEngine.BASELINE_B2C_ONEHOT64,  # [ENUM-MERGE] B2c zero-training floor probe
            EmbeddingEngine.CHECK2HGI_CTLE,  # [ENUM-MERGE] B1 CTLE contextual per-visit substrate
            EmbeddingEngine.BASELINE_B2A_POI2VEC,  # [ENUM-MERGE] B2a faithful POI2Vec
            EmbeddingEngine.BASELINE_GEOTREE_SKIPGRAM,  # [ENUM-MERGE] geo-tree skip-gram baseline
            # integrity_v2 study engines. next_region.parquet is copied from check2hgi_dk_ovl,
            # subset to the same rows in the same order; load_next_region's userid-equality
            # guard verifies that alignment on every load.
            EmbeddingEngine.CHECK2HGI_IV2_STRICT,
            EmbeddingEngine.CHECK2HGI_IV2_CAUSAL,
            # v18 run (2026-08-06): region task is in scope, so the engine must be here as
            # well as in the enum + MTL allowlist — a category-only registration trains fine
            # and then fails at the region tower.
            EmbeddingEngine.CHECK2HGI_V18,
            # [2026-08-16] Q13, o controle de concatenacao. As duas engines de place embedding
            # entram aqui porque o braco de CATEGORIA tambem passa por load_next_region, e o
            # carregador le dessa tabela apenas region_idx e last_region_idx: rotulos derivados do
            # mapa POI->regiao e do janelamento, nao do substrato de embedding. As tabelas foram
            # copiadas de check2hgi_dk_ovl, mesmas linhas na mesma ordem, sob o janelamento atual,
            # e a guarda de igualdade de userid abaixo verifica esse alinhamento a cada carga.
            # Mesmo argumento e mesma mecanica ja usados pelas engines do estudo integrity_v2.
            EmbeddingEngine.HGI_DK_OVL,
            EmbeddingEngine.HGI_OVL_FEAT,
        )
        if embedd_engine not in supported:
            raise ValueError(
                f"next_region not yet built for {embedd_engine}. Supported: "
                f"{[e.name for e in supported]}. Build with "
                f"scripts/probe/build_hgi_next_region.py (or analogous)."
            )
        return cls.get_input_dir(state, embedd_engine) / "next_region.parquet"

    @classmethod
    def load_next_region(cls, state: str, embedd_engine: EmbeddingEngine) -> DataFrame:
        """Load next-region input data for a state (CHECK2HGI only)."""
        return pd.read_parquet(cls.get_next_region(state, embedd_engine))

    @classmethod
    def load_next(cls, state: str, embedd_engine: EmbeddingEngine) -> DataFrame:
        """Load next-POI input data for a specific state and engine."""
        return pd.read_parquet(cls.get_next(state, embedd_engine))

    @classmethod
    def get_seq_next(cls, state: str, embedd_engine: EmbeddingEngine):
        if embedd_engine == EmbeddingEngine.FUSION:
            return cls.get_fusion_seq_next(state)
        return OUTPUT_DIR / embedd_engine.value / state.lower() / "temp" / "sequences_next.parquet"

    @classmethod
    def get_results_dir(cls, state, embedd_engine: EmbeddingEngine) -> Path:
        """Get results directory (routes FUSION automatically)."""
        if embedd_engine == EmbeddingEngine.FUSION:
            return cls.get_fusion_results_dir(state)
        return RESULTS_ROOT / embedd_engine.value / state.lower()

    @classmethod
    def get_folds_dir(cls, state, embedd_engine: EmbeddingEngine) -> Path:
        """Get folds directory (routes FUSION automatically)."""
        if embedd_engine == EmbeddingEngine.FUSION:
            return cls.get_fusion_folds_dir(state)
        return OUTPUT_DIR / embedd_engine.value / state.lower() / "folds"

    # ========================================================================
    # Multi-Embedding Fusion Paths
    # ========================================================================

    @staticmethod
    def get_fusion_input_dir(state: str) -> Path:
        """Get directory for fusion-based inputs."""
        return OUTPUT_DIR / "fusion" / state.lower() / "input"

    @staticmethod
    def get_fusion_category(state: str) -> Path:
        """Get path to fused category input."""
        return IoPaths.get_fusion_input_dir(state) / "category.parquet"

    @staticmethod
    def load_fusion_category(state: str) -> DataFrame:
        """Load fused category input."""
        return pd.read_parquet(IoPaths.get_fusion_category(state))

    @staticmethod
    def get_fusion_next(state: str) -> Path:
        """Get path to fused next-POI input."""
        return IoPaths.get_fusion_input_dir(state) / "next.parquet"

    @staticmethod
    def load_fusion_next(state: str) -> DataFrame:
        """Load fused next-POI input."""
        return pd.read_parquet(IoPaths.get_fusion_next(state))

    @staticmethod
    def get_fusion_seq_next(state: str) -> Path:
        """Get path to intermediate sequences for fusion."""
        return IoPaths.get_fusion_input_dir(state) / "temp" / "sequences_next.parquet"

    @staticmethod
    def get_fusion_results_dir(state: str) -> Path:
        """Get results directory for fusion experiments."""
        return RESULTS_ROOT / "fusion" / state.lower()

    @staticmethod
    def get_fusion_folds_dir(state: str) -> Path:
        """Get folds directory for fusion experiments."""
        return OUTPUT_DIR / "fusion" / state.lower() / "folds"



