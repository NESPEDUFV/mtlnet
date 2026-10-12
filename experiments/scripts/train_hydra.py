"""Optional Hydra entrypoint for MTLnet training.

Provides Hydra-based config composition and CLI overrides.
Delegates to the canonical scripts/train.py for actual training.

Requires: pip install hydra-core omegaconf
If hydra is not installed, this script prints an error and exits.

Usage:
    python scripts/train_hydra.py
    python scripts/train_hydra.py state=alabama engine=hgi
    python scripts/train_hydra.py epochs=10 folds=2
    python scripts/train_hydra.py --multirun state=florida,alabama

The existing scripts/train.py remains the canonical entrypoint.
This is a convenience wrapper for Hydra users.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ and scripts/ are on sys.path
_scripts = str(Path(__file__).resolve().parent)
_src = str(Path(__file__).resolve().parent.parent / "src")
if _scripts not in sys.path:
    sys.path.insert(0, _scripts)
if _src not in sys.path:
    sys.path.insert(0, _src)

try:
    import hydra
    from omegaconf import DictConfig
except ImportError:
    print(
        "Error: hydra-core is not installed.\n"
        "Install it with: pip install hydra-core omegaconf\n"
        "Or use the standard entrypoint: python scripts/train.py --help",
        file=sys.stderr,
    )
    sys.exit(1)


# Resolve config path relative to this file
_CONFIG_DIR = str(Path(__file__).resolve().parent.parent / "experiments" / "hydra_configs")


@hydra.main(version_base=None, config_path=_CONFIG_DIR, config_name="train")
def main(cfg: DictConfig) -> None:
    """Hydra entrypoint that delegates to scripts/train.main()."""
    from train import main as train_main

    # Build argv from Hydra config to pass to the argparse-based train.main()
    argv = [
        "--state", str(cfg.state),
        "--engine", str(cfg.engine),
        "--task", str(cfg.task),
        "--epochs", str(cfg.epochs),
        "--folds", str(cfg.folds),
    ]

    train_main(argv)


if __name__ == "__main__":
    main()
