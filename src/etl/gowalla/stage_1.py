import logging

import pandas as pd
import numpy as np
import json
import re

from src.configs.paths import Resources, IoPaths

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("label_categories.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



def extract_category_name(category_str):
    """
    Extract the 'name' value from a category string representation.

    Parameters:
        category_str (str): String representation of the category dictionary.

    Returns:
        str or np.nan: The extracted category name, or np.nan if not found.
    """
    if not isinstance(category_str, str):
        return np.nan
    match = re.search(r"name':\s*(['\"])(.*?)\1", category_str)
    return match.group(2) if match else np.nan


def build_super_categories_mapping(data, initial_mapping=None):
    """
    Build a mapping from category names to super categories using JSON data.

    Parameters:
        data (dict): JSON data containing category structures.
        initial_mapping (dict, optional): Initial mapping to update. Defaults to None.

    Returns:
        dict: A mapping from category names to super categories.
    """
    if initial_mapping is None:
        initial_mapping = {}

    super_categories_dict = initial_mapping.copy()

    for category in data.get('spot_categories', []):
        super_category_name = category.get('name').strip()
        for subcategory in category.get('spot_categories', []):
            subcategory_name = subcategory.get('name').strip()
            super_categories_dict[subcategory_name] = super_category_name
            for sub_subcategory in subcategory.get('spot_categories', []):
                sub_subcategory_name = sub_subcategory.get('name').strip()
                super_categories_dict[sub_subcategory_name] = super_category_name

    return super_categories_dict


def label_categories():
    """
    This function reads the check-ins data, cleans it, and saves it to a Parquet file.
    """
    logger.info("Starting label_categories train.")


    '''Reading the original checkins'''
    if Resources.CHECKINS_PARQUET.exists():
        checking_ori = pd.read_parquet(Resources.CHECKINS_PARQUET)
        logger.info(f"Loaded check-ins from Parquet: {len(checking_ori)} records.")
    else:
        # WARNING: This will take 1'+ to load
        checking_ori = pd.read_csv(
            Resources.CHECKINS,
            dtype={'userid': 'int64', 'placeid': 'int64'},
            parse_dates=['datetime'],
            date_format="%Y-%m-%dT%H:%M:%SZ",
            low_memory=False
        )
        logger.info(f"Loaded check-ins from CSV: {len(checking_ori)} records.")

    '''Remove duplicate check-ins from the raw data'''
    dupes_count = checking_ori.duplicated(subset=['userid', 'placeid', 'datetime']).sum()
    if dupes_count > 0:
        checking_ori = checking_ori.drop_duplicates(subset=['userid', 'placeid', 'datetime'])
        logger.info(f"Removed {dupes_count} duplicate check-ins. Remaining: {len(checking_ori)} records.")

    '''Reading Map of Places to Categories'''
    # Load the category structure from the JSON file
    with open(Resources.CATEGORIES_STRUCTURE, 'r') as f:
        data = json.load(f)

    # Load the super and extra categories from the JSON files
    # This categories complement the categories structure from gowalla
    super_categories = json.load(open(Resources.CATEGORIES_CALLBACK, 'r'))
    #TODO: [IMPROVE]
    extra_categories = json.load(open(Resources.EXTRA_CATEGORIES_CALLBACK, 'r'))
    # extra_categories = {}

    # Build the complete super categories mapping
    super_categories_dict = build_super_categories_mapping(data, {**super_categories, **extra_categories})
    logger.info(f"Built super categories mapping with {len(super_categories_dict)} entries.")

    '''Read points of interest (POIs) data'''
    # Read points of interest (POIs) data this dataset contains the most detailed information about the POIs
    pois_details = pd.read_csv(Resources.SPOTS)
    pois_details.rename(
        columns={
            'id': 'placeid',
            'lat': 'latitude',
            'lng': 'longitude',
        },
        inplace=True
    )
    pois_details.set_index('placeid', inplace=True)

    # Read points of interest (POIs) data this dataset DOES NOT contain many details about the POIs
    # But we can use it to get the category name
    pois_not_details = pd.read_csv(Resources.SPOTS_2, encoding="latin1")
    pois_not_details.rename(
        columns={
            'id': 'placeid',
            'lat': 'latitude',
            'lng': 'longitude',
            'name': 'spot'
        },
        inplace=True
    )
    pois_not_details = pois_not_details.drop_duplicates(subset='placeid')
    pois_not_details = pois_not_details[['placeid', 'latitude', 'longitude', 'spot']]
    pois_not_details.set_index('placeid', inplace=True)

    # Creating a boolean column 'detailed': True for pois_details, False for pois_not_details
    # This will be useful to clean the data after if necessary
    pois_details['detailed'] = True
    pois_not_details['detailed'] = False

    ''''Extracting the spot(Nome do Local) from pois_detail and merger the pois'''
    # Extract category names from the 'category' field
    pois_details['spot'] = pois_details['spot_categories'].apply(extract_category_name)

    # Fill the pois with placeid from pois_2 that are not in pois
    pois_merged = pois_details.combine_first(pois_not_details)
    logger.info(f"Merged POIs dataset has {pois_merged.shape[0]} records.")

    '''Merge check-ins with POIs on `placeid`'''
    checkins_pois = checking_ori.merge(pois_merged, on='placeid', how='inner', validate='m:1')
    logger.info(f"After merging, check-ins dataset has {checkins_pois.shape[0]} records. Loss: {len(checking_ori) - len(checkins_pois)}")

    '''Map the spot to the super category'''
    # Trail white space from category_name
    checkins_pois['spot'] = checkins_pois['spot'].str.strip()

    # Map category names to super categories
    checkins_pois['category'] = checkins_pois['spot'].map(super_categories_dict)

    '''Missing spots'''
    missing_spot = checkins_pois[checkins_pois.category.isna()]['spot'].value_counts()
    missing_spot_str = ', '.join([f"{spot}({count})" for spot, count in missing_spot.items()])
    logger.info(f"Missing categories ({len(missing_spot)})")

    '''drop rows with na categories'''
    checking_final = checkins_pois.dropna(subset=['category'])
    logger.info(f"Dropped rows with missing categories. Final check-ins count: {len(checking_final)} (Loss: {len(checking_ori) - len(checking_final)})")

    # Save the cleaned check-ins data to a Parquet file
    checking_final.to_parquet(IoPaths.CHECKINS_ETL_STEP_1)
    logger.info(f"Saved cleaned check-ins data to {IoPaths.CHECKINS_ETL_STEP_1}.")

    return checking_final

if __name__ == "__main__":
    label_categories()