import geopandas as gp


def geo_merge(gdf_points, gdf_countries):
    merged = gp.sjoin(gdf_countries, gdf_points, how='inner', predicate='contains')
    if 'index_right' in merged.columns:
        merged.rename(columns={'index_right': 'index'}, inplace=True)
    merged.set_index('index', inplace=True)
    merged.sort_index(inplace=True)

    left_out = gdf_points[~gdf_points.index.isin(merged.index)]

    return merged, left_out