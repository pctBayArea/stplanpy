#!/usr/bin/python3

import pandas as pd
import pandas_flavor as pf
from shapely.geometry import LineString

@pf.register_dataframe_method
def od_lines(fd: pd.DataFrame, centroids: pd.DataFrame, orig="orig_taz", dest="dest_taz") -> pd.DataFrame:
    
    def lines(*x):
        p0 = centroids.loc[x[0]]
        p1 = centroids.loc[x[1]]
        return LineString([p0, p1])
    
    df = fd[[orig, dest]].apply(lambda x: lines(*x), axis=1)

    return df
