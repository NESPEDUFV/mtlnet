"""Check2HGI Pipeline — train check-in-level embeddings, generate inputs. Usage: python pipelines/embedding/check2hgi.pipe.py"""

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
from configs.paths import Resources, EmbeddingEngine
from configs.model import InputsConfig
from embeddings.check2hgi.check2hgi import create_embedding
from data.inputs.builders import generate_next_input_from_checkins

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# SETTINGS
# =============================================================================

MAX_WORKERS = 1

# =============================================================================
# CONFIG
# =============================================================================

CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM,
    num_layers=2,
    attention_head=4,
    alpha_c2p=0.4,
    alpha_p2r=0.3,
    alpha_r2c=0.3,
    lr=0.001,
    gamma=1.0,
    max_norm=0.9,
    epoch=500,
    mini_batch_threshold=5_000_000,
    batch_size=2**13,
    num_neighbors=10,
    device='cpu',
    shapefile=None,
    force_preprocess=True,
    edge_type='user_sequence',
    temporal_decay=3600.0,
    use_compile=True,
    use_amp=False,
)

# =============================================================================
# STATES
# Ordered dict — execution follows insertion order, MAX_WORKERS at a time.
# Each entry: 'StateName': {'shapefile': <Resource>, ...overrides, 'config': <Namespace>}
# When 'config' key is absent, CONFIG (default) is used.
# =============================================================================

STATES = {
    # AL + FL already generated in a prior run; AZ added for probe triangulation.
    # 'Alabama': {'shapefile': Resources.TL_AL},
    # 'Florida': {'shapefile': Resources.TL_FL},
    'Arizona': {'shapefile': Resources.TL_AZ},
    # 'Georgia': {'shapefile': Resources.TL_GA},
    # 'California': {'shapefile': Resources.TL_CA},
    # 'Texas': {'shapefile': Resources.TL_TX},
}

# =============================================================================
# PIPELINE
# =============================================================================


def process_state(name: str, state_cfg: dict) -> bool:
    """Run Check2HGI pipeline for a single state (check-in-level, no category input)."""
    try:
        state_cfg = dict(state_cfg)
        base = state_cfg.pop('config', CONFIG)
        config = copy(base)
        config.shapefile = state_cfg.pop('shapefile')
        for k, v in state_cfg.items():
            setattr(config, k, v)

        logger.info(f"[1/2] Creating embeddings (preprocess + train): {name}")
        create_embedding(state=name, args=config)

        logger.info(f"[2/2] Generating next-POI inputs: {name}")
        generate_next_input_from_checkins(name, EmbeddingEngine.CHECK2HGI)

        return True
    except Exception as e:
        logger.error(f"Failed processing {name}: {e}", exc_info=True)
        return False


def run_pipeline():
    """Process all configured states in order, MAX_WORKERS at a time."""
    logger.info(f"Check2HGI Pipeline - {len(STATES)} state(s) | device={DEVICE} | dim={CONFIG.dim}")

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
