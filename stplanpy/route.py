r"""
Route operations
"""
import warnings
import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
from shapely.geometry import Point
from shapely.geometry import LineString

@pf.register_dataframe_method
def directness(fd: pd.DataFrame, geom="geometry") -> pd.DataFrame:
    r"""
    Compute directness of a route
    """    
    def direct(x):
# Compute distance along route
        rt_dist = x.length

# Extract begin and end longitude and latitude of each geometry
        x0 = Point(x.coords[0]).x
        y0 = Point(x.coords[0]).y
        x1 = Point(x.coords[-1]).x
        y1 = Point(x.coords[-1]).y

# Compute distance along od line        
        ln_dist = LineString([(x0,y0), (x1,y1)]).length

        if (ln_dist == 0):
            return 1.0
        else:
            return rt_dist/ln_dist
    
    return fd[geom].apply(lambda x: direct(x))

@pf.register_dataframe_method
def reduce(fd: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    r"""
    Reduce route network
    """
# Ignore UserWarning from overlay function below
    warnings.filterwarnings("ignore", category=UserWarning)


    gdf0 = fd
    gdf1 = fd
    gdf2 = fd

    i = 0
    cont = True
    i_max = gdf0.shape[0]
    while (cont):
        gdf_tmp = gdf0.drop([gdf0.index[i]]).overlay(gdf0.iloc[[i]], how="intersection")
        if not gdf_tmp.empty:
            gdf0 = gdf_tmp
            gdf0.rename(columns = {"all_1":"all"}, inplace = True)
            gdf0.rename(columns = {"bike_1":"bike"}, inplace = True)
            gdf0.loc[0, "all"]  = gdf0.loc[0, "all"]  + gdf0.loc[0, "all_2" ]
            gdf0.loc[0, "bike"] = gdf0.loc[0, "bike"] + gdf0.loc[0, "bike_2"]
            gdf0 = gdf0.drop(columns="all_2")
            gdf0 = gdf0.drop(columns="bike_2")

            gdf1 = gdf1.iloc[[i]].overlay(gdf1.drop([gdf1.index[i]]), how="difference")
          
            gdf2 = gdf2.drop([gdf2.index[i]]).overlay(gdf2.iloc[[i]], how="difference")

            gdf0 = gdf0.explode(ignore_index=True)
            gdf1 = gdf1.explode(ignore_index=True)
            gdf2 = gdf2.explode(ignore_index=True)

            frames = [gdf0, gdf1, gdf2]
            gdf0 = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry='geometry')
            gdf1 = gdf0
            gdf2 = gdf0

            i = 0
            i_max = gdf0.shape[0]

        i += 1
        if (i < i_max):
            cont = True
        else:
            cont = False

    return gdf0
