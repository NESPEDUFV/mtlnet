#!/usr/bin/env python3
"""Fusion Pipeline — generate fused multi-embedding inputs. Usage: python pipelines/fusion.pipe.py"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
_research = str(_root / "research")
if _src not in sys.path:
    sys.path.insert(0, _src)
if _research not in sys.path:
    sys.path.insert(0, _research)

from configs.embedding_fusion import get_preset
from configs.paths import IoPaths
from data.inputs.fusion import MultiEmbeddingInputGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# SETTINGS
# =============================================================================

MAX_WORKERS = 2  # Fusion is memory-intensive
FUSION_PRESET = "space_hgi_time"  # Options: space_hgi_time, hgi_time, space_time

# =============================================================================
# STATES
# Ordered dict — execution follows insertion order, MAX_WORKERS at a time.
# Optional 'preset' override per state (defaults to FUSION_PRESET above).
# =============================================================================

STATES = {
    'arizona': {},
    'florida': {},

    'alabama': {},
    'california': {},
    'texas': {},

}


# =============================================================================
# PIPELINE
# =============================================================================


def process_state(state: str, state_cfg: dict) -> bool:
    """Generate fusion inputs for a single state."""
    try:
        preset = state_cfg.get('preset', FUSION_PRESET)

        fusion_config = get_preset(preset)
        logger.info(
            f"[{state}] preset='{preset}' | "
            f"cat_dim={fusion_config.get_category_dim()} | next_dim={fusion_config.get_next_dim()}"
        )

        generator = MultiEmbeddingInputGenerator(state, fusion_config)

        category_path = IoPaths.get_fusion_category(state)
        sequences_path = IoPaths.get_fusion_seq_next(state)
        next_path = IoPaths.get_fusion_next(state)

        category_path.parent.mkdir(parents=True, exist_ok=True)
        sequences_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"[{state}] [1/2] Generating category input...")
        generator.generate_category_input(str(category_path))

        logger.info(f"[{state}] [2/2] Generating next-POI input...")
        generator.generate_next_input(str(sequences_path), str(next_path))

        generator.loader.clear_cache()

        logger.info(f"[{state}] Complete")
        return True

    except Exception as e:
        logger.error(f"[{state}] Failed: {e}", exc_info=True)
        return False


def run_pipeline() -> dict:
    """Process all configured states in order, MAX_WORKERS at a time."""
    logger.info(f"Fusion Pipeline - {len(STATES)} state(s) | preset={FUSION_PRESET}")

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


if __name__ == "__main__":
    results = run_pipeline()
    exit(0 if all(results.values()) else 1)
