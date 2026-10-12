"""Space2Vec Pipeline — train spatial embeddings, generate inputs. Usage: python pipelines/embedding/space2vec.pipe.py"""

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

import torch
from configs.globals import DEVICE
from configs.paths import EmbeddingEngine
from configs.model import InputsConfig
from embeddings.space2vec.space2vec import create_embedding
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
    spa_embed_dim=128,
    freq_num=16,
    max_radius=50,
    min_radius=0.02,
    epoch=40,
    batch_size=256,
    lr=3e-4,
    r_pos_km=10.0,
    r_neg_km=70.0,
    k_pos_per_i=8,
    k_neg_per_i=16,
    hard_neg_ratio=0.0,
    tau=0.15,
    max_grad_norm=1.0,
    seed=42,
    device=DEVICE,
    force_pairs=True,
    use_torch_encoder=True,
    no_torch_encoder=False,
    loss_type="bce",
    deduplicate=True,
    compile=True,
    max_pairs=None,
    block_size=500_000,
    amp=True,
)

# =============================================================================
# STATES
# Ordered dict — execution follows insertion order, MAX_WORKERS at a time.
# Each entry: 'StateName': {...overrides, 'config': <Namespace>}
# When 'config' key is absent, CONFIG (default) is used.
# =============================================================================

STATES = {
    'Alabama': {},
    'Arizona': {},
    'Georgia': {},
    'Florida': {},
    'California': {},
    'Texas': {},
}

# =============================================================================
# PIPELINE
# =============================================================================


def process_state(name: str, state_cfg: dict) -> bool:
    """Run Space2Vec pipeline for a single state."""
    try:
        state_cfg = dict(state_cfg)
        base = state_cfg.pop('config', CONFIG)
        config = copy(base)
        for k, v in state_cfg.items():
            setattr(config, k, v)

        # Ensure device is torch.device
        if isinstance(config.device, str):
            config.device = torch.device(config.device)

        logger.info(f"[1/1] Creating embeddings: {name}")
        create_embedding(state=name, args=config)

        # Uncomment to generate inputs after embedding creation:
        # generate_category_input(name, EmbeddingEngine.SPACE2VEC)
        # generate_next_input_from_poi(name, EmbeddingEngine.SPACE2VEC)

        return True
    except Exception as e:
        logger.error(f"Failed processing {name}: {e}", exc_info=True)
        return False


def run_pipeline():
    """Process all configured states in order, MAX_WORKERS at a time."""
    logger.info(f"Space2Vec Pipeline - {len(STATES)} state(s) | device={DEVICE} | dim={CONFIG.dim}")

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
