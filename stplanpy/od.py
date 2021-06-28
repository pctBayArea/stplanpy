import numpy as np
import pandas as pd
import pandas_flavor as pf
from shapely.geometry import LineString

@pf.register_dataframe_method
def od_lines(fd: pd.DataFrame, centroids: pd.DataFrame, orig="orig_taz", dest="dest_taz") -> pd.DataFrame:
    
    def lines(*x):
        p0 = centroids.loc[x[0], "geometry"]
        p1 = centroids.loc[x[1], "geometry"]
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
            p0 = elevation.loc[x[0]].values[0]
            p1 = elevation.loc[x[1]].values[0]
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
    fd = fd.merge(cnt, how="left", left_on="orig_taz",right_index=True)
    fd.rename(columns = {"countyfp":"orig_cnt"}, inplace = True)
    fd = fd.merge(cnt, how="left", left_on="dest_taz",right_index=True)
    fd.rename(columns = {"countyfp":"dest_cnt"}, inplace = True)

# Merge on placefp codes
    fd = fd.merge(plc, how="left", left_on="orig_taz",right_index=True)
    fd.rename(columns = {"placefp":"orig_plc"}, inplace = True)
    fd = fd.merge(plc, how="left", left_on="dest_taz",right_index=True)
    fd.rename(columns = {"placefp":"dest_plc"}, inplace = True)

# Clean up data frame
    fd.drop(columns=list(fd.filter(regex="_x|_y")), inplace=True)
    fd.fillna(value="", inplace=True)

    return fd
