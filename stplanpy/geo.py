import numpy as np
import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
from shapely.geometry import Point, Polygon, MultiPolygon, GeometryCollection

def read_shp(file_name, crs="EPSG:6933"):
    r"""
    Read shape files
    """
    gdf = gpd.read_file(file_name)
    gdf = gdf.to_crs(crs)
    gdf.columns = gdf.columns.str.lower()

    return gdf

@pf.register_dataframe_method
def to_geojson(gdf: gpd.GeoDataFrame, file_name, crs="EPSG:4326"):
    r"""
    Write GeoDataFrame to GeoJson file
    """
    gdf.to_crs(crs).to_file(file_name, driver="GeoJSON")

@pf.register_dataframe_method
def in_county(plc: gpd.GeoDataFrame, cnt: gpd.GeoDataFrame, area_min=0.1) -> gpd.GeoDataFrame:
    r"""
    Check in which county a place is located
    """
    plc["area"] = plc["geometry"].area
    plc = gpd.overlay(plc, cnt, how="intersection")
    plc["area"] = plc["geometry"].area/plc["area"]

# Drop surface areas that are too small
    plc = plc[plc["area"] > area_min]

# Clean up column names
    plc.rename(columns = {"name_1":"name"}, inplace = True)
    plc = plc[["placefp", "name", "countyfp", "geometry"]]

    return plc

@pf.register_dataframe_method
def in_place(taz: gpd.GeoDataFrame, plc: gpd.GeoDataFrame, area_min=0.001, area_thr=0.9999) -> gpd.GeoDataFrame:
    r"""
    Check in which place a traffic analysis zone (TAZ) is located
    """
# Compute surface areas and overlay    
    taz["area"] = taz["geometry"].area
    taz_plc = gpd.overlay(taz, plc, how="intersection")
    taz_plc["area"] = taz_plc["geometry"].area/taz_plc["area"]

# Set very similar surface areas to one    
    taz_plc.loc[taz_plc["area"] > area_thr, "area"] = 1.0
# Drop surface areas that are too small
    taz_plc = taz_plc[taz_plc["area"] > area_min]

# If taz is not in place, placefp is np.nan
# If taz is only partly in place, countyfp is np.nan and there is another row
# which lists the complete taz with a valid countyfp

# Merge data frames   
    taz["area"] = 1.0
    taz = taz[["tazce", "countyfp", "geometry", "area"]]
    taz_plc = taz_plc[["tazce", "placefp", "geometry", "area"]]
    taz_plc = taz_plc.merge(taz, left_on=["tazce", "area"], right_on=["tazce", "area"],  how="outer", suffixes=(None, "_"))

# Fix geometry
    taz_plc.loc[taz_plc["geometry"] == None, "geometry"] = taz_plc["geometry_"]

# Drop unwanted columns
    taz_plc = taz_plc[["tazce", "countyfp", "placefp", "geometry", "area"]]
    
    return taz_plc

@pf.register_dataframe_method
def cent(gdf: gpd.GeoDataFrame, index_name="tazce") -> gpd.GeoDataFrame:
    r"""
    Compute centroids
    """
    return gpd.GeoDataFrame(gdf[index_name], geometry=gdf.centroid, crs="EPSG:6933")

@pf.register_dataframe_method
def corr_cent(gdf: gpd.GeoDataFrame, index, lon, lat, index_name="tazce", crs="EPSG:4326", to_crs="EPSG:6933") -> gpd.GeoDataFrame:
    r"""
    Correct a centroids
    """
    corr = Point(lon, lat)
    corr = gpd.GeoSeries([corr], crs=crs)
    corr = corr.to_crs(to_crs)

    gdf.loc[gdf[index_name] == index, "geometry"] = corr.loc[0]
      
    return gdf
