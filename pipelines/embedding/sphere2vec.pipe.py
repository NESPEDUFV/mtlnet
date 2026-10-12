"""Sphere2Vec Pipeline — train spatial embeddings (SphereMixScale), generate inputs. Usage: python pipelines/embedding/sphere2vec.pipe.py"""

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
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_category_input, generate_next_input_from_poi
from embeddings.sphere2vec.sphere2vec import create_embedding

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# SETTINGS
# =============================================================================

MAX_WORKERS = 1

# =============================================================================
# CONFIG
# =============================================================================

# Paper-faithful SphereMixScale (Eq.8, Mai et al. 2023). Adopted as default after
# Alabama ablation showed rbf vs paper are statistically tied, but paper has ~half
# the std and ~35% faster training. See sphere2vec/README.md for full ablation.
# To revert to notebook's rbf: encoder_variant='rbf', batch_size=64, legacy_dataset=True
CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM,
    spa_embed_dim=128,
    num_scales=32,
    min_scale=10,
    max_scale=1e7,
    num_centroids=256,
    min_radius=10.0,
    max_radius=10000.0,
    ffn_hidden_dim=512,
    ffn_num_hidden_layers=1,
    ffn_dropout_rate=0.5,
    ffn_act="relu",
    ffn_use_layernormalize=True,
    ffn_skip_connection=True,
    epoch=50,
    batch_size=4096,  # 9x faster on MPS vs notebook's bs=64
    lr=1e-3,
    tau=0.15,
    pos_radius=0.01,
    seed=42,
    num_workers=0, #MPS 0 workers
    eval_batch_size=10000,
    device=DEVICE,
    legacy_dataset=False,
    encoder_variant="paper",
    eval_inference=False,
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
    """Run Sphere2Vec pipeline for a single state."""
    try:
        state_cfg = dict(state_cfg)
        base = state_cfg.pop('config', CONFIG)
        config = copy(base)
        for k, v in state_cfg.items():
            setattr(config, k, v)

        # Ensure device is torch.device
        if isinstance(config.device, str):
            config.device = torch.device(config.device)

        logger.info(f"[1/3] Creating embeddings: {name}")
        create_embedding(state=name, args=config)

        logger.info(f"[2/3] Generating category input: {name}")
        generate_category_input(name, EmbeddingEngine.SPHERE2VEC)

        logger.info(f"[3/3] Generating next-POI input: {name}")
        generate_next_input_from_poi(name, EmbeddingEngine.SPHERE2VEC)

        return True
    except Exception as e:
        logger.error(f"Failed processing {name}: {e}", exc_info=True)
        return False


def run_pipeline():
    """Process all configured states in order, MAX_WORKERS at a time."""
    logger.info(f"Sphere2Vec Pipeline - {len(STATES)} state(s) | device={DEVICE} | dim={CONFIG.dim}")

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
