#!/usr/bin/python3

import geopandas as gpd
from shapely.geometry import Point

def corr_cent(lon, lat):
    
    corr = Point(lon, lat)
    corr = gpd.GeoDataFrame(geometry=[corr], crs="EPSG:4326")
    corr = corr.to_crs("EPSG:6933")

    return corr["geometry"].values[0]
