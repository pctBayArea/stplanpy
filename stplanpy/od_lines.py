#!/usr/bin/python3

import pandas as pd
import pandas_flavor as pf
from shapely.geometry import LineString

@pf.register_dataframe_method
def od_lines(fd: pd.DataFrame, centroids: pd.DataFrame) -> pd.DataFrame:
    
    def f(*x):
        p0 = centroids.loc[x[0]]
        p1 = centroids.loc[x[1]]
        return LineString([p0, p1])
    
    df = fd[["orig_taz", "dest_taz"]].apply(lambda x: f(*x), axis=1)

    return df
