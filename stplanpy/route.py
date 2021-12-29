r"""
The functions in this module perform various operations on routes.
"""
import warnings
import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
from shapely.ops import linemerge
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import MultiLineString
from shapely.errors import ShapelyDeprecationWarning

@pf.register_dataframe_method
def directness(fd: gpd.GeoDataFrame, geom="geometry") -> pd.Series:
    r"""
    Compute the directness of a route

    This function computes the directness of the routes in GeoDataFrame `fd`.
    Directness is defined as the distance along a route divided by the distance
    as the crow flies. `geom` is the column name that contains the routes and
    defaults to "geometry".

    Parameters
    ----------
    geom : str, defaults to "geometry"
        Name of the column containing the routes.

    Returns
    -------
    pandas.Series
        Series with directness values.

    See Also
    --------
    ~stplanpy.cycle.routes

    Examples
    --------
    .. code-block:: python

        import pandas as pd
        import geopandas as gpd
        from shapely import wkt
        from stplanpy import route

        # Create DataFrames
        df = pd.DataFrame(
            {"all": [4, 3, 2, 5],
            "bike": [2, 0, 1, 3],
            "go_dutch": [3, 5, 0, 4],
            "geometry": ["LINESTRING(1 0,0 0,1 1,2 1,3 0)",
            "LINESTRING(0 2,1 1,2 1,3 2,2 2)",
            "LINESTRING(1 0,1 1,2 1,2 0)",
            "LINESTRING(1 2,1 1,2 1,2 2,3 2)"]})

        # Convert to WTK
        df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry')

        # Compute directness
        gdf["directness"] = gdf.directness()

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
def network(fd: gpd.GeoDataFrame, geom="geometry", modes=["bike", "go_dutch"]) -> gpd.GeoDataFrame:
    r"""
    Reduce route data to a network

    This function reduces route data in GeoDataFrame `fd` to a network for the
    modes of transporation listed in `modes`. The column name `geom` contains
    the routes and defaults to "geometry". All line segments of routes that
    overlap are reduced to one segment and their mode numbers are summed up.

    Parameters
    ----------
    geom : str, defaults to "geometry"
        Name of the column containing the routes.
    modes : list of str, defaults to ["bike", "go_dutch"]
        List of modes of transportation that the network is computed for.
        Defaults to ["bike", "go_dutch"].

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame containing the network.

    See Also
    --------
    ~stplanpy.cycle.routes

    Examples
    --------
    .. code-block:: python

        mport pandas as pd
        port geopandas as gpd
        om shapely import wkt
        om stplanpy import route

        Create DataFrames
        df = pd.DataFrame(
            {"all": [4, 3, 2, 5],
            "bike": [2, 0, 1, 3],
            "go_dutch": [3, 5, 0, 4],
            "geometry": ["LINESTRING(1 0,0 0,1 1,2 1,3 0)",
            "LINESTRING(0 2,1 1,2 1,3 2,2 2)",
            "LINESTRING(1 0,1 1,2 1,2 0)",
            "LINESTRING(1 2,1 1,2 1,2 2,3 2)"]})

        # Convert to WTK
        df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry')

        # Compute the network
        network = gdf.network()
    """
# Ignore shapely warning while using version 1.8
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

# Drop all columns except geom and modes
    mode = modes.copy()
    mode.append(geom)
    gdf = fd[mode]

# Drop all columns where all modes are zero
    gdf = gdf.loc[gdf[modes].values.sum(axis=1) != 0]

# Drop all non LineString gometries 
    gdf = gdf.loc[gdf.geom_type == "LineString"]

    def segments(curve):
        return MultiLineString(list(map(LineString, zip(curve.coords[:-1], curve.coords[1:]))))

# Break up routes into line segments
    gdf["geometry"] = fd[geom].apply(lambda x: segments(x))
    gdf = gdf.explode(ignore_index=True)

    def reverse(line):
        if (line.coords[0][0] > line.coords[1][0]):
            return True 
        else:
            return False

# Set reverse direction                                         
    gdf["reverse"] = gdf["geometry"].apply(lambda x: reverse(x))

    def direction(*x):
        if ([1]):
            return LineString([x[0].coords[1], x[0].coords[0]])
        else:
            return x[0]

# Align all segments in the same direction
    gdf["geometry"] = gdf[["geometry", "reverse"]].apply(lambda x: direction(*x), axis=1)

    def point_x0(line):
        return line.coords[0][0]

    def point_y0(line):
        return line.coords[0][1]

    def point_x1(line):
        return line.coords[1][0]

    def point_y1(line):
        return line.coords[1][1]

# Extract the individual longitudes and lattitudes so groupby function can be
# used
    gdf["x0"] = gdf["geometry"].apply(lambda x: point_x0(x))
    gdf["y0"] = gdf["geometry"].apply(lambda x: point_y0(x))
    gdf["x1"] = gdf["geometry"].apply(lambda x: point_x1(x))
    gdf["y1"] = gdf["geometry"].apply(lambda x: point_y1(x))

# Sum duplicate entries using groupby
    for mode in modes:
        gdf[mode] = gdf.groupby(["x0", "y0", "x1", "y1"])[mode].transform("sum")

# Realign all segments
    gdf["geometry"] = gdf[["geometry", "reverse"]].apply(lambda x: direction(*x), axis=1)

# Drop duplicates and extra columns
    gdf = gdf.drop_duplicates(subset=["x0", "y0", "x1", "y1"])
    gdf.drop(["x0", "y0", "x1", "y1", "reverse"], axis=1, inplace=True)

# Dissolve elements
    gdf = gdf.dissolve(by=modes, as_index=False)

# Drop empty geometries
    gdf = gdf[~gdf.is_empty] 

    def merge(multi_line):
        if (multi_line.geom_type == "MultiLineString"):
            return linemerge(multi_line)
        else:
            return multi_line

# Merge line segments
    gdf["geometry"] = gdf["geometry"].apply(lambda x: merge(x))

    return gdf
