"""MTL training pipeline — train multi-task model via scripts/train.py. Usage: python pipelines/train/mtl.pipe.py"""

import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

_root = Path(__file__).resolve().parent.parent.parent
_train = str(_root / "scripts" / "train.py")
sys.path.insert(0, str(_root / "src"))

from configs.paths import EmbeddingEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================================================
# SETTINGS
# =============================================================================

MAX_WORKERS = 1

# =============================================================================
# CONFIG
# =============================================================================

CONFIG = {
    'engine': EmbeddingEngine.FUSION.value,
    'embedding_dim': 128,
    'epochs': None,
    'folds': None,
}

# =============================================================================
# STATES
# Ordered dict — execution follows insertion order, MAX_WORKERS at a time.
# Each entry: 'StateName': {...overrides, 'config': <dict>}
# When 'config' key is absent, CONFIG (default) is used.
# =============================================================================

STATES = {
    # 'alabama': {},
    # 'arizona': {},
    # 'georgia': {},
    'florida': {},
    # 'california': {},
    # 'texas': {},
}

# =============================================================================
# PIPELINE
# =============================================================================


def process_state(name: str, state_cfg: dict) -> bool:
    """Train MTL model for a single state via scripts/train.py."""
    try:
        state_cfg = dict(state_cfg)
        base = dict(state_cfg.pop('config', CONFIG))
        base.update(state_cfg)

        cmd = [sys.executable, _train, "--state", name, "--engine", base['engine'], "--task", "mtl"]
        if base.get('embedding_dim') is not None:
            cmd += ["--embedding-dim", str(base['embedding_dim'])]
        if base.get('epochs') is not None:
            cmd += ["--epochs", str(base['epochs'])]
        if base.get('folds') is not None:
            cmd += ["--folds", str(base['folds'])]

        logger.info(f"[{name}] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd)

        if result.returncode != 0:
            logger.error(f"[{name}] Failed with return code {result.returncode}")
            return False
        return True
    except Exception as e:
        logger.error(f"[{name}] Failed: {e}", exc_info=True)
        return False


def run_pipeline():
    """Process all configured states in order, MAX_WORKERS at a time."""
    logger.info(f"MTL Training Pipeline - {len(STATES)} state(s) | engine={CONFIG['engine']}")

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
