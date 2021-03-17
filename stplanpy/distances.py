#!/usr/bin/python3

import pandas as pd
import pandas_flavor as pf

@pf.register_dataframe_method
def distances(fd: pd.DataFrame) -> pd.DataFrame:
    
    def f(x):
        return x.length
    
    df = fd["geometry"].apply(lambda x: f(x))

    return df
