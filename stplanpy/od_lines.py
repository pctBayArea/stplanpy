#!/usr/bin/python3

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

def od_lines(flow_data, centroids):
    
    flow_data["geometry"] = ""
    flow_data["gradient"] = 0.0
    flow_data["distance"] = np.nan

    for i, fd in flow_data.iterrows():
        p0 = centroids.loc[flow_data.loc[i,"orig_taz"]]
        p1 = centroids.loc[flow_data.loc[i,"dest_taz"]]
        flow_data.loc[i,"geometry"] = LineString([p0, p1])
        flow_data.loc[i,"distance"] = flow_data.loc[i,"geometry"].length

# Set crs
    flow_data = gpd.GeoDataFrame(flow_data)
    flow_data = flow_data.set_crs("EPSG:6933")

    return flow_data
