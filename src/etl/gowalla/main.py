"""
Gowalla ETL — main orchestrator.

Pipeline (3 stages):

    Stage 1  →  load raw check-ins, label POIs with super-categories.
    Stage 2  →  attach `local_datetime` via timezone polygons.
    Stage 3  →  spatial-join check-ins with U.S. state polygons,
                 emit one CSV per state under data/checkins/.

Usage (standalone):
    python -m src.etl.gowalla.main

Or import and call:
    from src.etl.gowalla.main import run
    run()

Outputs are skipped when the corresponding artefact already exists, so the
pipeline is resumable. Pass ``force=True`` to recompute.

Required raw inputs (paths defined in src/configs/paths.py → Resources):
    Resources.CHECKINS_PARQUET            gowalla_checkins.parquet
    Resources.SPOTS                       gowalla_spots_subset1.csv
    Resources.SPOTS_2                     gowalla_spots_subset2.csv
    Resources.CATEGORIES_STRUCTURE        gowalla_category_structure.json
    Resources.CATEGORIES_CALLBACK         callback_categories.json
    Resources.EXTRA_CATEGORIES_CALLBACK   extra_categories.json
    Resources.STATES_US                   tl_2022_us_state.shp  (Census TIGER)
    Resources.TIMEZONES                   combined-shapefile-with-oceans.shp
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from src.configs.paths import IoPaths, Resources
from src.etl.gowalla import stage_1, stage_2, stage_3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def _check_raw_inputs() -> None:
    """Fail fast with a clear message if any required raw file is missing."""
    required = {
        "CHECKINS_PARQUET": Resources.CHECKINS_PARQUET,
        "SPOTS": Resources.SPOTS,
        "SPOTS_2": Resources.SPOTS_2,
        "CATEGORIES_STRUCTURE": Resources.CATEGORIES_STRUCTURE,
        "CATEGORIES_CALLBACK": Resources.CATEGORIES_CALLBACK,
        "EXTRA_CATEGORIES_CALLBACK": Resources.EXTRA_CATEGORIES_CALLBACK,
    }
    missing = {name: path for name, path in required.items() if not path.exists()}
    if missing:
        details = "\n".join(f"  {name}: {path}" for name, path in missing.items())
        raise FileNotFoundError(
            "Gowalla ETL is missing required raw inputs:\n"
            f"{details}\n\n"
            "Place the raw Gowalla files under data/gowalla/ — see "
            "src/etl/gowalla/main.py docstring for the expected layout."
        )


def run(*, force: bool = False, skip_localise: bool = False) -> pd.DataFrame:
    """Run the Gowalla ETL end-to-end.

    Parameters
    ----------
    force
        Recompute every stage even when its output artefact already exists.
    skip_localise
        Skip stage 2 (timezone-based local_datetime). Set to True when the
        timezone shapefile is unavailable; downstream training does not need
        ``local_datetime`` for the BRACIS pipeline.
    """
    _check_raw_inputs()

    IoPaths.CHECKINS_ETL_STEP_1.parent.mkdir(parents=True, exist_ok=True)

    # Stage 1 — categorise
    if force or not IoPaths.CHECKINS_ETL_STEP_1.exists():
        logger.info("Stage 1 — labelling categories.")
        stage_1.label_categories()
    else:
        logger.info("Stage 1 cached at %s — skipping.", IoPaths.CHECKINS_ETL_STEP_1)

    # Stage 2 — attach local_datetime
    if skip_localise:
        logger.info("Stage 2 skipped (skip_localise=True).")
    elif force or not IoPaths.CHECKINS_ETL_STEP_2.exists():
        if not Resources.TIMEZONES.exists():
            raise FileNotFoundError(
                f"Timezone shapefile missing: {Resources.TIMEZONES}\n"
                "Either download the timezone-boundary-builder release "
                "(combined-shapefile-with-oceans) into data/miscellaneous/, "
                "or run with skip_localise=True."
            )
        logger.info("Stage 2 — localising check-ins to local_datetime.")
        stage_2.localize_checkins()
    else:
        logger.info("Stage 2 cached at %s — skipping.", IoPaths.CHECKINS_ETL_STEP_2)

    # Stage 3 — split per state
    if not skip_localise and (force or not IoPaths.CHECKINS_ETL_STEP_3.exists()):
        if not Resources.STATES_US.exists():
            raise FileNotFoundError(
                f"US states shapefile missing: {Resources.STATES_US}\n"
                "Download tl_2022_us_state from "
                "https://www2.census.gov/geo/tiger/TIGER2022/STATE/ "
                "into data/miscellaneous/."
            )
        logger.info("Stage 3 — splitting check-ins per U.S. state.")
        stage_3.checking_states()
    elif skip_localise:
        logger.warning(
            "Stage 3 needs CHECKINS_ETL_STEP_2 from stage 2; "
            "you ran with skip_localise=True so per-state outputs are not produced."
        )
    else:
        logger.info("Stage 3 cached at %s — skipping.", IoPaths.CHECKINS_ETL_STEP_3)

    if IoPaths.CHECKINS_ETL_STEP_3.exists():
        return pd.read_parquet(IoPaths.CHECKINS_ETL_STEP_3)
    if IoPaths.CHECKINS_ETL_STEP_2.exists():
        return pd.read_parquet(IoPaths.CHECKINS_ETL_STEP_2)
    return pd.read_parquet(IoPaths.CHECKINS_ETL_STEP_1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gowalla ETL pipeline")
    parser.add_argument("--force", action="store_true", help="Recompute every stage.")
    parser.add_argument(
        "--skip-localise",
        action="store_true",
        help="Skip stage 2 (timezone-based local_datetime).",
    )
    args = parser.parse_args()
    df = run(force=args.force, skip_localise=args.skip_localise)
    print(f"\nFinal row count: {len(df):,}")
