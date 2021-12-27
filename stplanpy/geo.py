r"""
This module performs various operations on geospatial vector data. Shapefiles of
traffic analysis zones (`TAZ`_), places, and counties can be found `online`_.

.. _TAZ: https://catalog.data.gov/dataset/tiger-line-shapefile-2011-series-information-file-for-the-2010-census-traffic-analysis-zone-taz

.. _online: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
"""
import os
import warnings
import glob
import shutil
import zipfile
import numpy as np
import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
from shapely.geometry import Point, Polygon, MultiPolygon, GeometryCollection

def read_shp(file_name, tmp_dir="tmp", crs="EPSG:6933"):
    r"""
    Read (zipped) shape files 

    Read (zipped) shape files into a GeoDataFrame with a number of default
    options. The coordinate reference system (crs) defaults to "EPSG:6933" and
    all the column names are made lower case.

    Parameters
    ----------
    file_name : str
        Name and path of the (zipped) shape file.
    tmp_dir : str, defaults to "tmp"
        Name of temporary directory to extract the zip archive to.
    crs : str, defaults to "EPSG:6933"
        The coordinate reference system (crs) of the output GeoDataFrame. The
        default value is "EPSG:6933".
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataframe with all the column names found in the shape file inside
        the zip achive in lower case.
    
    See Also
    --------
    ~stplanpy.geo.to_geojson
    
    Examples
    --------
    The example data file, "`tl_2011_06_taz10.zip`_", can be downloaded from
    github. Read a shape file:
 
    .. code-block:: python

        import shutil
        import zipfile
        from stplanpy import geo

        # Extract to temporal location
        with zipfile.ZipFile("tl_2011_06_taz10.zip", "r") as zip_ref:
            zip_ref.extractall("tmp")
        
        # Read taz data from shp file
        taz = geo.read_shp("tmp/" + "tl_2011_06_taz10.shp")
        
        # Clean up tmp files
        shutil.rmtree("tmp")

    Read a shape file from a zip file:

    .. code-block:: python

        from stplanpy import geo

        # Read taz data from zip file
        taz = geo.read_shp("tl_2011_06_taz10.zip")

    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    """

    if (os.path.splitext(file_name)[1] == ".zip"):
        # Extract to temporal location
        with zipfile.ZipFile(file_name, "r") as zip_ref:
             zip_ref.extractall(tmp_dir)

        # find shape file
        shp_file = glob.glob("tmp/**/*.shp", recursive=True)
        if (len(shp_file) == 0):
            raise Exception("There is no shape file inside this zip archive")
        elif (len(shp_file) > 1):
            raise Exception("There is more than one shape file inside this zip archive")
    else:
        shp_file = [file_name]

    gdf = gpd.read_file(shp_file[0])
    gdf = gdf.to_crs(crs)
    gdf.columns = gdf.columns.str.lower()

    if (os.path.splitext(file_name)[1] == ".zip"):
        # Clean up files
        shutil.rmtree(tmp_dir)

    return gdf


@pf.register_dataframe_method
def to_geojson(gdf: gpd.GeoDataFrame, file_name, crs="EPSG:4326"):
    r"""
    Write GeoDataFrame to GeoJson file

    Write GeoDataFrame to a GeoJson file with the default coordinate reference
    system (crs) "EPSG:4326".

    Parameters
    ----------
    crs : str, defaults to "EPSG:4326"
        The coordinate reference system (crs) of the output GeoJson file. The
        default value is "EPSG:4326".
 
    Returns
    -------
    None
    
    See Also
    --------
    ~stplanpy.geo.read_shp
    
    Examples
    --------
    The example data file, "`tl_2011_06_taz10.zip`_", can be downloaded from github.
 
    .. code-block:: python

        from stplanpy import geo

        # Read taz data from zip file
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Write to file
        taz.to_geojson("taz.GeoJson")

    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    """
    gdf.to_crs(crs).to_file(file_name, driver="GeoJSON")

    return None

@pf.register_dataframe_method
def in_county(plc: gpd.GeoDataFrame, cnt: gpd.GeoDataFrame, area_min=0.1) -> gpd.GeoDataFrame:
    r"""
    Check in which county a place is located

    From one GeoDataFrame with places and one GeoDataFrame containing counties,
    this function computes in which county a place is situated. A threshold
    value is used to handle potential misalignment of the borders.

    Parameters
    ----------
    cnt : geopandas.GeoDataFrame
        GeoDataFrame with the county geometries in which the TAZ are located.
    area_min : float, defaults to 0.1
        If ratio of the surface area of a place inside a county devided by the
        full sarface area of a place is smaller than this threshold value, it is
        discarded. This is a workaround for geometries who's borders are not
        fully aligned.
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataframe with column names "placefp", "name", "countyfp", and
        "geometry". "countyfp" contains the index of the county.
    
    See Also
    --------
    ~stplanpy.geo.in_place
    
    Examples
    --------
    The example data files, "`ca-county-boundaries.zip`_" and "`tl_2020_06_place.zip`_", can be downloaded from github.
 
    .. code-block:: python

        from stplanpy import geo

        # Limit calculation to these counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read County data from zip file
        county = geo.read_shp("ca-county-boundaries.zip")

        # Filter on county codes
        county = county[county["countyfp"].isin(counties)]

        # Select columns to keep
        county = county[["name", "countyfp", "geometry"]]

        # Read Place data from zip file
        place = geo.read_shp("tl_2020_06_place.zip")

        # Rename to Mountain View, Martinez
        place.loc[(place["placefp"] == "49651"), "name"] = "Mountain View, Martinez"

        # Compute which places lay inside which county
        place = place.in_county(county)

    .. _ca-county-boundaries.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/ca-county-boundaries.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
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

    From one GeoDataFrame with traffic analysis zones (TAZ) and one GeoDataFrame
    containing places, this function computes in which place a TAZ is situated.
    Threshold values are used to handle potential misalignment of the borders.
    If a TAZ is situated across multiple places, additional rows are created
    for the parts that are situated within each place.

    Parameters
    ----------
    plc : geopandas.GeoDataFrame
        GeoDataFrame with the place geometries in which the TAZ are located.
    area_min : float, defaults to 0.001
        If ratio of the surface area of a TAZ inside a place devided by the
        full sarface area of a TAZ is smaller than this threshold value, it is
        discarded. This is a workaround for geometries who's borders are not
        fully aligned.
    area_thr : float, defaults to 0.9999
        If ratio of the surface area of a TAZ inside a place devided by the
        full sarface area of a TAZ is larger than this threshold value, it is
        considered completely located within this place. This is a workaround
        for geometries who's borders are not fully aligned.
 
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataframe with column names "tazce", "countyfp", "placefp",
        "geometry", en "area". "placefp" contains the index of the place.
    
    See Also
    --------
    ~stplanpy.geo.in_county
    
    Examples
    --------
    The example data files,"`tl_2020_06_place.zip`_" and "`tl_2011_06_taz10.zip`_", can be downloaded from github.
 
    .. code-block:: python

        from stplanpy import geo

        # Limit calculation to these counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read TAZ data from zip file
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Read Place data from zip file
        place = geo.read_shp("tl_2020_06_place.zip")

        # Compute which taz lay inside a place and which part
        taz = taz.in_place(place)

    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
    """

# Ignore UserWarning from overlay function below
    warnings.filterwarnings("ignore", category=UserWarning)

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
    column_name : str, defaults to "tazce"
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
 
        from stplanpy import geo
        
        # Limit calculation to these counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read TAZ data from zip file
        taz = geo.read_shp("tl_2011_06_taz10.zip")

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
        Index of the centroid that is modified.
    lon : float
        New longitude of the corrected centroid. The default coordinate
        reference system (crs) is "EPSG:4326".
    lat : float
        New latitude of the corrected centroid. The default coordinate
        reference system (crs) is "EPSG:4326".
    index_name : str, defaults to "tazce"
        Name of the column that the `index` variable refers to. The default name
        is "tazce".
    crs : str, defaults to "EPSG:4326"
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
 
        from stplanpy import geo
        
        # Limit calculation to these counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read TAZ data from zip file
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # filter by county   
        taz = taz[taz["countyfp"].isin(counties)]

        # Compute centroids
        taz_cent = taz.cent()

        # Correct centroid location
        taz_cent.corr_cent("00101155", -122.078052, 37.423328)
    
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    """
    corr = Point(lon, lat)
    corr = gpd.GeoSeries([corr], crs=crs)
    corr = corr.to_crs(gdf.crs)

    gdf.loc[gdf[index_name] == index, "geometry"] = corr.loc[0]
      
    return gdf
