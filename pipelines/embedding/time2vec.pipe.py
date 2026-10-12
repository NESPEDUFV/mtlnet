"""Time2Vec Pipeline — train temporal embeddings, generate inputs. Usage: python pipelines/embedding/time2vec.pipe.py"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
_src = str(_root / "src")
_research = str(_root / "research")
if _src not in sys.path:
    sys.path.insert(0, _src)
if _research not in sys.path:
    sys.path.insert(0, _research)

import logging
from argparse import Namespace
from copy import copy
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

from configs.globals import DEVICE
from configs.paths import EmbeddingEngine
from configs.model import InputsConfig
from embeddings.time2vec.time2vec import create_embedding
from data.inputs.builders import generate_next_input_from_checkins

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# SETTINGS
# =============================================================================

MAX_WORKERS = 2

# =============================================================================
# CONFIG
# =============================================================================

CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM,
    out_features=64,
    activation='sin',
    lr=1e-3,
    epoch=100,
    batch_size=2048,
    r_pos_hours=1.0,
    r_neg_hours=24.0,
    max_pairs=2_000_000,
    k_neg_per_i=5,
    max_pos_per_i=20,
    seed=42,
    tau=0.3,
    device=DEVICE,  # MPS 2.4x faster than CPU with bs=2048 + compile
    compile=True,
    sampling_mode="feat_space",  # paper-faithful wrap-aware sampling (+0.81pp F1 vs legacy)
    r_pos_feat=0.03,
    r_neg_feat=0.30,
    no_train=False,
)

# =============================================================================
# STATES
# Ordered dict — execution follows insertion order, MAX_WORKERS at a time.
# Each entry: 'StateName': {...overrides, 'config': <Namespace>}
# When 'config' key is absent, CONFIG (default) is used.
# =============================================================================

STATES = {
    # ── Gowalla (US states) ─────────────────────────────────────────────────
    # 'Alabama': {},
    # 'Arizona': {},
    # 'Georgia': {},
    # 'Florida': {},
    # 'California': {},
    # 'Texas': {},
    # ── Foursquare TIST2015 ─────────────────────────────────────────────────
    'nyc_fsq':   {},
    'tokyo_fsq': {},
    # ── Massive-STEPS ───────────────────────────────────────────────────────
    'new_york_ms': {},
    'tokyo_ms':    {},
}

# =============================================================================
# PIPELINE
# =============================================================================


def process_state(name: str, state_cfg: dict) -> bool:
    """Run Time2Vec pipeline for a single state (check-in-level embeddings)."""
    try:
        state_cfg = dict(state_cfg)
        base = state_cfg.pop('config', CONFIG)
        config = copy(base)
        for k, v in state_cfg.items():
            setattr(config, k, v)

        logger.info(f"[1/2] Creating embeddings: {name}")
        create_embedding(state=name, args=config)

        logger.info(f"[2/2] Generating inputs: {name}")
        generate_next_input_from_checkins(name, EmbeddingEngine.TIME2VEC)

        return True
    except Exception as e:
        logger.error(f"Failed processing {name}: {e}", exc_info=True)
        return False


def run_pipeline():
    """Process all configured states in order, MAX_WORKERS at a time."""
    logger.info(f"Time2Vec Pipeline - {len(STATES)} state(s) | device={DEVICE} | dim={CONFIG.dim}")

    start = datetime.now()
    results = {}
    states = list(STATES.items())

    for i in range(0, len(states), MAX_WORKERS):
        chunk = states[i:i + MAX_WORKERS]
        if MAX_WORKERS == 1:
            for name, cfg in chunk:
                results[name] = process_state(name, cfg)
        else:
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {
                    executor.submit(process_state, name, dict(cfg)): name
                    for name, cfg in chunk
                }
                for future in as_completed(futures):
                    results[futures[future]] = future.result()

    duration = (datetime.now() - start).total_seconds()
    success = sum(results.values())
    logger.info(f"Completed: {success}/{len(STATES)} succeeded in {duration / 60:.1f}min")
    for name, ok in results.items():
        logger.info(f"  {'✓' if ok else '✗'} {name}")

    return results


if __name__ == '__main__':
    results = run_pipeline()
    exit(0 if all(results.values()) else 1)
