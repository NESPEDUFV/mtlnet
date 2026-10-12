import logging

import pandas as pd
import geopandas as gp
from tqdm import tqdm

from src.configs.paths import IoPaths, Resources
from src.etl.gowalla.utils import utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("segregate_checkins.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def checking_states():
    logger.info("Starting localization of check-ins.")

    # Delete the output file if it exists
    IoPaths.CHECKINS_ETL_STEP_3.unlink(missing_ok=True)

    """Load check-ins data from a Parquet file."""
    checkins_df = pd.read_parquet(IoPaths.CHECKINS_ETL_STEP_2)

    """Filter check-ins to include only those in the United States."""
    # checkins_us = checkins_df[
    #     checkins_df.country_name.str.contains('United States of America|USA', case=False, na=False)]

    checkins_us = checkins_df

    logger.info(f"Working with {len(checkins_us)} check-ins in the United States.")

    """Convert check-ins DataFrame to a GeoDataFrame."""
    gdf_us = gp.GeoDataFrame(
        checkins_us,
        geometry=gp.points_from_xy(checkins_us.longitude, checkins_us.latitude),
        crs="EPSG:4326"
    )[['userid', 'geometry']]

    """Load U.S. states shapefile and prepare it for spatial operations."""
    gdf_states = gp.read_file(Resources.STATES_US)[['NAME', 'geometry']]
    gdf_states.to_crs("EPSG:4326", inplace=True)
    gdf_states.rename(columns={'NAME': 'state_name'}, inplace=True)

    """Perform a spatial join to find points within polygons. """
    checkins_within_states, checkins_left_out = utils.geo_merge(gdf_us, gdf_states)
    logger.info("Matched %.2f%% of the check-ins with U.S. states.",
                len(checkins_within_states) / len(checkins_us) * 100)

    checkins_left_out_proj = checkins_left_out.to_crs("EPSG:3857")
    states_proj = gdf_states.to_crs("EPSG:3857")

    # logger.info("Performing a spatial join to find the nearest state for each of the left out")
    # """Perform a spatial join to find the nearest polygon for each point."""
    # checkins_nearest_states = gp.sjoin_nearest(
    #     checkins_left_out_proj,
    #     states_proj,
    #     max_distance=300,
    #     how='inner',
    #     distance_col='distance_to_nearest_state'
    # )
    # checkins_nearest_states.to_crs("EPSG:4326", inplace=True)
    # logger.info("Matched %.2f%% of the left-out with U.S. states.",
    #             len(checkins_nearest_states) / len(checkins_left_out) * 100)
    #
    # # Combine the within-states and nearest-states data
    # combined_checkins = pd.concat([checkins_within_states, checkins_nearest_states])

    # Add state information back to the original check-ins data
    final_checkins_us = checkins_us.join(
        checkins_within_states[['state_name']],
        validate='1:1',
        how='inner'
    )

    final_checkins_us["country_name"] = "United States of America"

    logger.info("Matched %.2f%% of the check-ins with U.S. states.", len(final_checkins_us) / len(checkins_us) * 100)

    # Save the final data to a Parquet file
    final_checkins_us.to_parquet(IoPaths.CHECKINS_ETL_STEP_3)
    final_checkins_us.to_csv(IoPaths.CHECKINS_ETL_STEP_3_CSV)

    # check dirs
    IoPaths.CHECKINS_ETL_STATES.mkdir(parents=True, exist_ok=True)
    IoPaths.CHECKINS_ETL_STATES_PARQUET.mkdir(parents=True, exist_ok=True)

    # create a parquet to each state
    for state in tqdm(final_checkins_us.state_name.unique(), desc="Saving check-ins by state"):
        state_df = final_checkins_us[final_checkins_us.state_name == state]
        state_df.to_csv(IoPaths.CHECKINS_ETL_STATES / f"{state}.csv", index=False)
        # state_df.to_parquet(IoPaths.CHECKINS_ETL_STATES_PARQUET / f"{state}.parquet")
        logger.info(f"Saved {len(state_df)} check-ins for {state} - {len(state_df)}.")


if __name__ == "__main__":
    checking_states()
