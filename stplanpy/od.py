r"""
The functions in this module perform various operations on origin-denstination
or flow data.
"""
import warnings
import numpy as np
import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
from shapely.geometry import LineString
from shapely.errors import ShapelyDeprecationWarning

@pf.register_dataframe_method
def od_lines(fd: pd.DataFrame, centroids: pd.DataFrame, orig="orig_taz", dest="dest_taz") -> pd.DataFrame:
    r"""
    Compute origin-destination lines.

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
# Ignore ShapelyDeprecationWarning
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

    def lines(*x):
        p0 = centroids.loc[centroids["tazce"] == x[0], "geometry"].iloc[0]
        p1 = centroids.loc[centroids["tazce"] == x[1], "geometry"].iloc[0]
        return LineString([p0, p1])
    
    return fd[[orig, dest]].apply(lambda x: lines(*x), axis=1)

@pf.register_dataframe_method
def distances(fd: pd.DataFrame) -> pd.DataFrame:
    
    def f(x):
        return x.length
    
    df = fd["geometry"].apply(lambda x: f(x))

    return df

@pf.register_dataframe_method
def gradient(fd: pd.DataFrame, elevation: pd.DataFrame, orig="orig_taz", 
        dest="dest_taz", dist="distance") -> pd.DataFrame:
    
    def grad(*x):
        if (x[2] == 0):
            return 0.0
        else:
            p0 = elevation.loc[elevation["tazce"] == x[0], "elevation"].iloc[0]
            p1 = elevation.loc[elevation["tazce"] == x[1], "elevation"].iloc[0]
            return np.absolute((p1 - p0) / x[2])
    
    return fd[[orig, dest, dist]].apply(lambda x: grad(*x), axis=1)

@pf.register_dataframe_method
def orig_dest(fd: pd.DataFrame, taz: pd.DataFrame) -> pd.DataFrame:

# Drop lines that have no valid countyfp or placefp. i.e. are not within a
# county or place
    cnt = taz.dropna(subset=["countyfp"])
    plc = taz.dropna(subset=["placefp"])
# We do not know the distribution of origins or destinations within a TAZ.
# Therefore, add TAZ to place if more than 0.5 of its surface area is within
# this place.
    plc = plc.loc[plc["area"] > 0.5]

# Merge on countyfp codes
    fd = fd.merge(cnt, how="left", left_on="orig_taz",right_on="tazce")
    fd.rename(columns = {"countyfp":"orig_cnt"}, inplace = True)
    fd = fd.drop(columns=["tazce", "placefp", "geometry", "area"])
    fd = fd.merge(cnt, how="left", left_on="dest_taz",right_on="tazce")
    fd.rename(columns = {"countyfp":"dest_cnt"}, inplace = True)
    fd = fd.drop(columns=["tazce", "placefp", "geometry", "area"])

# Merge on placefp codes
    fd = fd.merge(plc, how="left", left_on="orig_taz",right_on="tazce")
    fd.rename(columns = {"placefp":"orig_plc"}, inplace = True)
    fd = fd.drop(columns=["tazce", "countyfp", "geometry", "area"])
    fd = fd.merge(plc, how="left", left_on="dest_taz",right_on="tazce")
    fd.rename(columns = {"placefp":"dest_plc"}, inplace = True)
    fd = fd.drop(columns=["tazce", "countyfp", "geometry", "area"])

# Clean up data frame
    fd.fillna(value="", inplace=True)

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
