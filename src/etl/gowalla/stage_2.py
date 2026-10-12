import pandas as pd
import geopandas as gp
import logging

from src.configs.paths import IoPaths, Resources
from src.etl.gowalla.utils import utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("localize_checkins.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def localize_checkins():
    logger.info("Starting localization of check-ins.")

    # Delete the output file if it exists
    IoPaths.CHECKINS_ETL_STEP_2.unlink(missing_ok=True)

    checkins = pd.read_parquet(IoPaths.CHECKINS_ETL_STEP_1)
    logger.info(f"Readed check-ins from {IoPaths.CHECKINS_ETL_STEP_1} | {len(checkins)} check-ins.")
    gdf = gp.GeoDataFrame(checkins, geometry=gp.points_from_xy(checkins.longitude, checkins.latitude), crs="EPSG:4326")[
        ['datetime', 'geometry']]

    # Remove outlier latitudes and longitudes
    gdf = gdf[gdf.geometry.y.between(-90, 90)]
    gdf = gdf[gdf.geometry.x.between(-180, 180)]

    """Converting the datetime to local datetime"""
    df_timezone = add_local_datetime(gdf)

    """Getting the countries"""
    # osm_gdf = add_countries(gdf)

    '''Save the df_timezone to a parquet file'''
    checkins_final = checkins.join(df_timezone[['local_datetime']], validate='1:1', how='inner')
    # checkins_final = checkins_final.join(osm_gdf[['country_name']], validate='1:1', how='inner')

    # Drop rows where country_name is NA
    # Probably the point is in location that is between two countries or in the ocean
    # IDEA: We should group user by location, but we shouldn't exclude the points of these users that are outside the location
    # checkins_final = checkins_final.dropna(subset=['country_name'])

    total_loss = len(checkins) - len(checkins_final)
    logger.info(f"Total loss after joins: {total_loss} check-ins.")

    checkins_final.to_parquet(IoPaths.CHECKINS_ETL_STEP_2)
    logger.info("Localization of check-ins completed successfully.")


def add_local_datetime(gdf):
    logger.info("Converting the datetime to local datetime.")

    timezones = gp.read_file(Resources.TIMEZONES)
    timezones.to_crs("EPSG:4326", inplace=True)

    df_timezone = gp.sjoin(timezones, gdf, predicate='contains')

    # drop geometry column, set index and remove duplicates
    df_timezone = df_timezone.drop(columns='geometry')

    df_timezone.rename(columns={'index_right': 'index'}, inplace=True)
    df_timezone.set_index('index', inplace=True)
    df_timezone.sort_index(inplace=True)

    # Some places have more than one timezone, so we need to remove duplicates
    df_timezone = df_timezone[~df_timezone.index.duplicated(keep='first')]

    # Convert each datetime using zip for better performance
    df_timezone['local_datetime'] = [
        # It's necessary to convert string to remove the t aware, otherwise the to_datetime will parse it as UTC time zone
        dt.tz_localize('UTC').tz_convert(tz).strftime('%Y-%m-%d %H:%M:%S')
        for dt, tz in zip(df_timezone['datetime'], df_timezone['tzid'])
    ]

    df_timezone['local_datetime'] = pd.to_datetime(df_timezone['local_datetime'])
    return df_timezone


def add_countries(gdf):
    logger.info("Getting the countries.")

    # May use more than one source of countries will garantee that more points will be localized
    # But matching the countries names will be more difficult
    osm_countries = gp.read_file(Resources.WORLD_OSM)[['adm0_name', 'geometry']]
    osm_countries.to_crs("EPSG:4326", inplace=True)
    osm_countries.rename(columns={'adm0_name': 'country_name'}, inplace=True)

    # Merge with OSM countries
    osm_gdf, osm_left_out = utils.geo_merge(gdf, osm_countries)
    print("OSM - Left out: ", len(osm_left_out))

    return osm_gdf


if __name__ == "__main__":
    localize_checkins()
