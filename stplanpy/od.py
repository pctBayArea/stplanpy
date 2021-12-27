r"""
The functions in this module perform various operations on origin-denstination
or flow data.
"""
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.errors import ShapelyDeprecationWarning

@pf.register_dataframe_method
def od_lines(fd: gpd.GeoDataFrame, centroids: gpd.GeoDataFrame, orig="orig_taz",
        dest="dest_taz") -> gpd.GeoSeries:
    r"""
    Compute origin-destination lines

    Compute origin-destination lines for all origin-destination pairs in
    GeoDataFrame `fd`. The `centroids` GeoDataFrame contains the coordinates of
    all the origins and destinations.
    
    Parameters
    ----------
    centroids: geopandas.GeoDataFrame
        GeoDataFrame with the coordinates of all the locations in the `fd`
        GeoDataFrame.
    orig : str, defaults to "orig_taz"
        Column name of the `fd` GeoDataFrame containing all origin codes.
    dest : str, defaults to "dest_taz"
        Column name of the `fd` GeoDataFrame containing all destination codes.
    
    Returns
    -------
    geopandas.GeoSeries
        GeoSeries with origin-destination lines 
    
    See Also
    --------
    ~stplanpy.od.orig_dest
    ~stplanpy.geo.cent
    
    Examples
    --------
    The example data files: "`od_data.csv`_", "`tl_2011_06_taz10.zip`_", and
    "`tl_2020_06_place.zip`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs
        from stplanpy import geo
        from stplanpy import od

        # Read origin-destination flow data
        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs()

        # San Francisco Bay Area counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Place code East Palo Alto
        places = ["20956"]

        # Read place data
        place = geo.read_shp("tl_2020_06_place.zip")

        # Keep only East Palo Alto
        place = place[place["placefp"].isin(places)]

        # Read taz data
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Compute centroids
        taz_cent = taz.cent()

        # Compute which taz lay inside a place and which part
        taz = taz.in_place(place)

        # Add county and place codes to data frame.
        flow_data = flow_data.orig_dest(taz)

        # Compute origin-destination lines
        flow_data["geometry"] = flow_data.od_lines(taz_cent)

    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
    """
# Ignore shapely warning while using version 1.8
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

    def lines(*x):
        x0 = centroids.loc[centroids["tazce"] == x[0], "geometry"].iloc[0].x
        y0 = centroids.loc[centroids["tazce"] == x[0], "geometry"].iloc[0].y
        x1 = centroids.loc[centroids["tazce"] == x[1], "geometry"].iloc[0].x
        y1 = centroids.loc[centroids["tazce"] == x[1], "geometry"].iloc[0].y
        return LineString([(x0,y0), (x1,y1)])   
    
    return gpd.GeoSeries(fd[[orig, dest]].apply(lambda x: lines(*x), axis=1), crs=fd.crs)

@pf.register_dataframe_method
def distances(fd: gpd.GeoDataFrame, geom="geometry") -> pd.Series:
    r"""
    Compute distance along origin-destination lines or routes

    This function computes the distance along origin-destination (od) lines or routes
    in the `fd` GeoDataFrame. `geom` is the name of column containing the od lines
    or routes.
    
    Parameters
    ----------
    geom : str, defaults to "geometry"
        Name of the column containing the origin-destination lines or routes.
    
    Returns
    -------
    pandas.Series
        Series with distances
    
    See Also
    --------
    ~stplanpy.od.od_lines
    ~stplanpy.cycle.routes
    
    Examples
    --------
    .. code-block:: python

        import pandas as pd
        import geopandas as gpd
        from shapely import wkt
        from stplanpy import od

        # Define two origin-destination lines
        df = pd.DataFrame({
            "orig_taz" : ["73906", "00106"],
            "dest_taz" : ["00120", "04120"],
            "geometry": [
            "LINESTRING(-91785727.431 4453819.337, -11782276.436 4448452.023)",
            "LINESTRING(-11785787.392 4450797.573, -11787086.209 4449884.472)"]})

        # Convert to WTK
        df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:6933")

        # Compute distances
        gdf["distance"] = gdf.distances()
    
    """
    def f(x):
        return x.length
    
    return fd[geom].apply(lambda x: f(x))  

@pf.register_dataframe_method
def gradient(fd: gpd.GeoDataFrame, elevation: gpd.GeoDataFrame, orig="orig_taz",
        dest="dest_taz", dist_name="distance") -> pd.Series:
    r"""
    Compute the gradient along an origin-destination line or route

    This function computes the gradient, :math:`\nabla = h/d`, along an
    origin-destination line or route. :math:`d` is the distance and :math:`h` is
    the elevation change.
    
    Parameters
    ----------
    elevation : geopandas.GeoDataFrame
        GeoDataFrame with elevation information for all the begin and end points
        of the origin-destination lines or routes in the `fd` GeoDataFrame.
    orig : str, defaults to "orig_taz"
        Column name in the `fd` GeoDataFrame containing all origin codes.
    dest : str, defaults to "dest_taz"
        Column name in the `fd` GeoDataFrame containing all destination codes.
    dist_name : str, defaults to "distance"
        Column name in the `fd` GeoDataFrame containing distance information
    
    Returns
    -------
    pandas.Series
        Series with gradients
    
    See Also
    --------
    ~stplanpy.od.od_lines
    ~stplanpy.cycle.routes
    ~stplanpy.od.distances
    ~stplanpy.srtm.elev
    
    Examples
    --------
    The example data files: "`od_data.csv`_", "`tl_2011_06_taz10.zip`_", and
    "`srtm_12_05.zip`_" can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs
        from stplanpy import geo
        from stplanpy import od
        from stplanpy import srtm

        # Read origin-destination flow data
        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs()

        # San Francisco Bay Area counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read taz data
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Compute centroids
        taz_cent = taz.cent()

        # Compute elevations
        taz_cent = taz_cent.elev("srtm_12_05.zip")

        # Compute origin-destination lines
        flow_data["geometry"] = flow_data.od_lines(taz_cent)

        # Compute distances
        flow_data["distance"] = flow_data.distances()

        # Compute gradients
        flow_data["gradient"] = flow_data.gradient(taz_cent)

    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _srtm_12_05.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/srtm_12_05.zip
    """    
    def grad(*x):
        if (x[2] == 0):
            return 0.0
        else:
            p0 = elevation.loc[elevation["tazce"] == x[0], "elevation"].iloc[0]
            p1 = elevation.loc[elevation["tazce"] == x[1], "elevation"].iloc[0]
            return np.absolute((p1 - p0) / x[2])
    
    return fd[[orig, dest, dist_name]].apply(lambda x: grad(*x), axis=1)

@pf.register_dataframe_method
def orig_dest(fd: gpd.GeoDataFrame, taz: gpd.GeoDataFrame, taz_name="tazce",
        plc_name="placefp", cnt_name="countyfp") -> gpd.GeoDataFrame:
    r"""
    Add County and Place codes to origin-destination data           

    This function adds County and Census Designated Place codes from the
    GeoDataFrame `taz` to the origin-destination or flow GeoDataFrame `fd`. The
    relevant column names are defined in `taz_name`, `plc_name`, and `cnt_name`,
    respectively. The column names in the output GeoDataFrame are "orig_taz",
    "dest_taz", "orig_plc", "dest_plc", "orig_cnt", and "dest_cnt". 
    
    Parameters
    ----------
    taz : geopandas.GeoDataFrame
        GeoDataFrame containing Traffic Analysis (TAZ) codes, Census Designated
        Place codes, and County codes.
    taz_name : str, defaults to "tazce"
        Column name in `taz` GeoDataFrame that contains TAZ codes. Defaults to
        "tazce".
    plc_name : str, defaults to "placefp"
        Column name in `taz` GeoDataFrame that contains Census Designated Place
        codes. Defaults to "placefp".
    cnt_name : str, defaults to "countyfp"
        Column name in `taz` GeoDataFrame that contains County codes. Defaults
        to "countyfp".
    
    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with origin and destination TAZ, County, and Place codes.
        The column names are "orig_taz", "dest_taz", "orig_plc", "dest_plc",
        "orig_cnt", and "dest_cnt". 
    
    See Also
    --------
    ~stplanpy.acs.read_acs
    ~stplanpy.geo.in_place
    
    Examples
    --------
    The example data files: "`od_data.csv`_", "`tl_2011_06_taz10.zip`_", and
    "`tl_2020_06_place.zip`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs
        from stplanpy import geo
        from stplanpy import od

        # Read origin-destination flow data
        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs()

        # San Francisco Bay Area counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Place code East Palo Alto
        places = ["20956"]

        # Read place data
        place = geo.read_shp("tl_2020_06_place.zip")

        # Keep only East Palo Alto
        place = place[place["placefp"].isin(places)]

        # Read taz data
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Compute which taz lay inside a place and which part
        taz = taz.in_place(place)

        # Add county and place codes to data frame.
        flow_data = flow_data.orig_dest(taz)

    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
    """
# Drop lines that have no valid countyfp or placefp. i.e. are not within a
# county or place
    cnt = taz.dropna(subset=[cnt_name])
    cnt = cnt.drop(columns = "geometry")
    plc = taz.dropna(subset=[plc_name])
    plc = plc.drop(columns = "geometry") 
# We do not know the distribution of origins or destinations within a TAZ.
# Therefore, add TAZ to place if more than 0.5 of its surface area is within
# this place.
    plc = plc.loc[plc["area"] > 0.5]

# Merge on countyfp codes
    fd = fd.merge(cnt, how="left", left_on="orig_taz",right_on=taz_name)
    fd.rename(columns = {cnt_name:"orig_cnt"}, inplace = True)
    fd = fd.drop(columns=[taz_name, plc_name, "area"])
    fd = fd.merge(cnt, how="left", left_on="dest_taz",right_on=taz_name)
    fd.rename(columns = {cnt_name:"dest_cnt"}, inplace = True)
    fd = fd.drop(columns=[taz_name, plc_name, "area"])

# Merge on placefp codes
    fd = fd.merge(plc, how="left", left_on="orig_taz",right_on=taz_name)
    fd.rename(columns = {plc_name:"orig_plc"}, inplace = True)
    fd = fd.drop(columns=[taz_name, cnt_name, "area"])
    fd = fd.merge(plc, how="left", left_on="dest_taz",right_on=taz_name)
    fd.rename(columns = {plc_name:"dest_plc"}, inplace = True)
    fd = fd.drop(columns=[taz_name, cnt_name, "area"])

# Clean up data frame
    fd.fillna({"orig_plc":"", "dest_plc":""}, inplace=True)

    return fd

@pf.register_dataframe_method
def mode_share(gdf: gpd.GeoDataFrame, flow_data: gpd.GeoDataFrame, modes=["bike", "go_dutch"], orig=None, dest=None, code=None) -> pd.DataFrame:
    r"""
    Compute mode share

    Compute origin-destination lines for all origin-destination pairs in
    dataframe `fd`. The `centroids` dataframe contains the coordinates of all the
    origins and destinations.
    
    Parameters
    ----------
    centroids: pd.DataFrame
    orig="orig_taz"
    dest="dest_taz"
    
    Returns
    -------
    pandas.DataFrame
        Cleaned up dataframe with origin destination data broken down by mode
    
    See Also
    --------
    ~stplanpy.acs.read_acs
    
    Examples
    --------
    The example data file, , can be downloaded from github.
    """
# Set origin, destination, and code column names    
    if (orig is None) and (dest is None) and (code is None):
        if ("countyfp" in gdf.columns) and  ("placefp" not in gdf.columns) and ("tazce" not in gdf.columns):
            orig="orig_cnt"
            dest="dest_cnt"
            code="countyfp"
        elif ("countyfp" in gdf.columns) and ("placefp" in gdf.columns) and ("tazce" in gdf.columns):
            orig="orig_taz"
            dest="dest_taz"
            code="tazce"
        elif ("placefp" in gdf.columns) and ("tazce" not in gdf.columns):
            orig="orig_plc"
            dest="dest_plc"
            code="placefp"
        else:
            raise Exception("GeoDataFrame is not recognized. Please specify orig, dest, and code variables")
    else:
        raise Exception("Please specify orig, dest, and code variables")

# Initialize
    df = gdf.loc[:,[code]]
    df["all"] = 0.0
    for mode in modes:
        df[mode] = 0.0
    
 # Total number of commute trips consistst of:
 # * trips that start and end in same location
 # * trips that start elsewhere and end at location
 # * trips that start at location and end elsewhere
    
    for index, row in df.iterrows():
#        print(row[code])
        fd = flow_data.loc[(flow_data[orig] == row[code]) | (flow_data[dest] == row[code])]
#        print(fd)
        if not fd.empty:
            df.loc[df[code] == row[code], "all"] = fd["all"].sum()
            for mode in modes:
                df.loc[df[code] == row[code], mode] = fd[mode].sum()
    
    for mode in modes:
        df[mode] /= df["all"]
        df[mode] = df[mode].fillna(0.0)
   
    return df[modes + ["all"]]

@pf.register_dataframe_method
def to(fd: gpd.GeoDataFrame, code) -> gpd.GeoDataFrame:
    r"""
    To
    """
    length = len(code)

    if (length == 3):
        dest = "dest_cnt"
    elif (length == 5):
        dest = "dest_plc"
    elif (length == 8):
        dest = "dest_taz"
    else:
        raise Exception("code not recognized")

    return fd.loc[fd[dest] == code]

@pf.register_dataframe_method
def frm(fd: gpd.GeoDataFrame, code) -> gpd.GeoDataFrame:
    r"""
    From
    """
    length = len(code)

    if (length == 3):
        orig = "orig_cnt"
    elif (length == 5):
        orig = "orig_plc"
    elif (length == 8):
        orig = "orig_taz"
    else:
        raise Exception("code not recognized")

    return fd.loc[fd[orig] == code]

@pf.register_dataframe_method
def to_frm(fd: gpd.GeoDataFrame, code) -> gpd.GeoDataFrame:
    r"""
    To from
    """
    length = len(code)

    if (length == 3):
        orig = "orig_cnt"
        dest = "dest_cnt"
    elif (length == 5):
        orig = "orig_plc"
        dest = "dest_plc"
    elif (length == 8):
        orig = "orig_taz"
        dest = "dest_taz"
    else:
        raise Exception("code not recognized")

    return fd.loc[(fd[orig] == code) | (fd[dest] == code)]

@pf.register_dataframe_method
def rm_taz(fd: gpd.GeoDataFrame, code, orig="orig_taz", dest="dest_taz"):
    r"""
    Remove TAZ
    """
    return fd.loc[(fd[orig] != code) & (fd[dest] != code)]
