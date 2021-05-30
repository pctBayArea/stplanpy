r"""
This module performs various operations on geospatial vector data. Shapefiles of
traffic analysis zones (`TAZ`_), places, and counties can be found `online`_.

.. _TAZ: https://catalog.data.gov/dataset/tiger-line-shapefile-2011-series-information-file-for-the-2010-census-traffic-analysis-zone-taz

.. _online: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
"""
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
def cent(gdf: gpd.GeoDataFrame, column_name="tazce") -> gpd.GeoDataFrame:
    r"""
    Compute centroids from a GeoDataFrame.

    This function computes the centroids of the geometries in a GeoDataFrame and
    returns them as a GeoDataFrame. By default the column name "tazce" is
    included in the new GeoDataFrame.

    Parameters
    ----------
    column_name : str
        Name of an input column to be included in the output GeoDataFrame. This
        value can also be a list of column names. The default column name is
        "tazce".
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataframe with centroids of the geometries in the input GeoDataFrame.
        The coordinate reference system (crs) of the output GeoDataFrame is the
        same as the input GeoDataframe.
    
    See Also
    --------
    ~stplanpy.geo.corr_cent
    
    Examples
    --------
    The example data file, "`tl_2011_06_taz10.zip`_", can be downloaded from github.
 
    .. code-block:: python
 
        import os
        import shutil
        import zipfile
        from stplanpy import geo
        
        # Limit calculation to these counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read taz
        # Extract to temporal location
        os.makedirs("tmp", exist_ok=True)
        with zipfile.ZipFile("tl_2011_06_taz10.zip", "r") as zip_ref:
            zip_ref.extractall("tmp")
        # Read shape file
        taz = geo.read_shp("tmp/tl_2011_06_taz10.shp")
        # Clean up tmp files
        shutil.rmtree("tmp")

        # Clean up taz GeoDataFrame
        # Rename columns
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)
        # filter by county   
        taz = taz[taz["countyfp"].isin(counties)]

        # Compute centroids
        taz_cent = taz.cent()
    
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    """
    return gpd.GeoDataFrame(gdf[column_name], geometry=gdf.centroid, crs=gdf.crs)

@pf.register_dataframe_method
def corr_cent(gdf: gpd.GeoDataFrame, index, lon, lat, index_name="tazce", crs="EPSG:4326") -> gpd.GeoDataFrame:
    r"""
    Correct centroid coordinates

    This function can be used to manually correct centroid positions computed
    using the :func:`~stplanpy.geo.cent` function. The required input parameters
    are the `index` of the centroid that is corrected, and the new longitude, `lon`, and
    latitude, `lat`.

    Parameters
    ----------
    index : str
        Index of the centroid that is modified
    lon : float
        New longitude of the corrected centroid. The default coordinate
        reference system (crs) is "EPSG:4326".
    lat : float
        New latitude of the corrected centroid. The default coordinate
        reference system (crs) is "EPSG:4326".
    index_name : str
        Name of the column that the `index` variable refers to. The default name
        is "tazce".
    crs : str
        Coordinate reference system (crs) of the `lon` and `lat` varibles. The
        default value is "EPSG:4326".
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataframe with corrected centroid. The coordinate reference system
        (crs) of the output GeoDataFrame is the same as the input GeoDataframe.
    
    See Also
    --------
    ~stplanpy.geo.cent
    
    Examples
    --------
    The example data file, "`tl_2011_06_taz10.zip`_", can be downloaded from github.
 
    .. code-block:: python
 
        import os
        import shutil
        import zipfile
        from stplanpy import geo
        
        # Limit calculation to these counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read taz
        # Extract to temporal location
        os.makedirs("tmp", exist_ok=True)
        with zipfile.ZipFile("tl_2011_06_taz10.zip", "r") as zip_ref:
            zip_ref.extractall("tmp")
        # Read shape file
        taz = geo.read_shp("tmp/tl_2011_06_taz10.shp")
        # Clean up tmp files
        shutil.rmtree("tmp")

        # Clean up taz GeoDataFrame
        # Rename columns
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)
        # filter by county   
        taz = taz[taz["countyfp"].isin(counties)]

        # Compute centroids
        taz_cent = taz.cent()

        # Correct centroid locations
        # Google plex
        taz_cent.corr_cent("00101155", -122.07805259936053, 37.42332894065777)
    
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    """
    corr = Point(lon, lat)
    corr = gpd.GeoSeries([corr], crs=crs)
    corr = corr.to_crs(gdf.crs)

    gdf.loc[gdf[index_name] == index, "geometry"] = corr.loc[0]
      
    return gdf
