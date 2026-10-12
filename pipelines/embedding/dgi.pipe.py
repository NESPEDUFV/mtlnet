"""DGI Pipeline — preprocess, train embeddings, generate inputs. Usage: python pipelines/embedding/dgi.pipe.py"""

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
from embeddings.dgi.dgi import create_embedding
from embeddings.dgi.preprocess import preprocess_dgi
from data.inputs.builders import generate_category_input, generate_next_input_from_poi

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
    lr=0.01,
    gamma=1.0,
    epoch=70,
    max_norm=0.9,
    device=DEVICE,
)

# =============================================================================
# STATES
# Ordered dict — execution follows insertion order, MAX_WORKERS at a time.
# Each entry: 'StateName': {'shapefile': <Resource>, ...overrides, 'config': <Namespace>}
# When 'config' key is absent, CONFIG (default) is used.
# =============================================================================

STATES = {
    'Alabama': {'shapefile': Resources.TL_AL},
    # 'Arizona': {'shapefile': Resources.TL_AZ},
    # 'Georgia': {'shapefile': Resources.TL_GA},
    # 'Florida': {'shapefile': Resources.TL_FL},
    # 'California': {'shapefile': Resources.TL_CA},
    # 'Texas': {'shapefile': Resources.TL_TX},
}

# =============================================================================
# PIPELINE
# =============================================================================


def process_state(name: str, state_cfg: dict) -> bool:
    """Run full DGI pipeline for a single state."""
    try:
        state_cfg = dict(state_cfg)
        base = state_cfg.pop('config', CONFIG)
        config = copy(base)
        shapefile = state_cfg.pop('shapefile')
        for k, v in state_cfg.items():
            setattr(config, k, v)

        logger.info(f"[1/3] Preprocessing: {name}")
        preprocess_dgi(city=name, city_shapefile=str(shapefile), cta_file=None)

        logger.info(f"[2/3] Creating embeddings: {name}")
        create_embedding(city=name, args=config)

        logger.info(f"[3/3] Generating inputs: {name}")
        generate_category_input(name, EmbeddingEngine.DGI)
        generate_next_input_from_poi(name, EmbeddingEngine.DGI)

        return True
    except Exception as e:
        logger.error(f"Failed processing {name}: {e}", exc_info=True)
        return False


def run_pipeline():
    """Process all configured states in order, MAX_WORKERS at a time."""
    logger.info(f"DGI Pipeline - {len(STATES)} state(s) | device={DEVICE} | dim={CONFIG.dim}")

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
