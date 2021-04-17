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
