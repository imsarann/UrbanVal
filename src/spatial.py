import numpy as np
import pandas as pd
import geopandas as gpd
from sklearn.neighbors import BallTree
from shapely.geometry import Point


def compute_transit_proximity(listings_df, subway_df, radius_km=1.0):
    subway_coords = subway_df[['GTFS Latitude', 'GTFS Longitude']].dropna()
    subway_rad = np.radians(subway_coords.values)
    listings_rad = np.radians(listings_df[['latitude', 'longitude']].values)

    tree = BallTree(subway_rad, metric='haversine')

    earth_radius_km = 6371.0
    dist_rad, _ = tree.query(listings_rad, k=1)
    distance_km = dist_rad.flatten() * earth_radius_km

    radius_rad = radius_km / earth_radius_km
    counts = tree.query_radius(listings_rad, r=radius_rad, count_only=True)

    result_df = listings_df.copy()
    result_df['distance_to_nearest_subway_km'] = np.round(distance_km, 3)
    result_df['subway_count_1km'] = counts
    return result_df


def spatial_join_neighborhoods(listings_df, geojson_path):
    geometry = [Point(xy) for xy in zip(listings_df['longitude'], listings_df['latitude'])]
    gdf_listings = gpd.GeoDataFrame(listings_df, geometry=geometry, crs="EPSG:4326")

    gdf_neighborhoods = gpd.read_file(geojson_path)
    if gdf_neighborhoods.crs != "EPSG:4326":
        gdf_neighborhoods = gdf_neighborhoods.to_crs("EPSG:4326")

    joined = gpd.sjoin(gdf_listings, gdf_neighborhoods, how="left", predicate="within")
    if 'index_right' in joined.columns:
        joined = joined.drop(columns=['index_right'])
    return pd.DataFrame(joined.drop(columns=['geometry']))
