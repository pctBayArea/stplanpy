r"""
The functions in this module are used to retrieve cycling routes from the `Cycle
Streets`_ website.

.. _Cycle Streets: https://www.cyclestreets.net
"""
import warnings
import re
import sys
import json
from requests_cache import CachedSession
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
import pandas as pd
import geopandas as gpd
import pandas_flavor as pf
from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.errors import ShapelyDeprecationWarning

@pf.register_dataframe_method
def routes(fd: gpd.GeoDataFrame, geom="geometry", api_key=None, plan="balanced", speed=20) -> gpd.GeoSeries:
    r"""
    Compute cycling routes

    This function takes origin-destination lines and computes a cycling route
    between them using the Cycling Streets router.
    
    Parameters
    ----------
    geom : str, defaults to "geometry"
        Name of the column that stores the origin-destination lines
    api_key : str, defaults to None
        Your registered API key
    plan : str, defaults to "balanced"
        The type of route, which can be one of the values: balanced, fastest,
        quietest. There is also shortest but see the notes below.

            - balanced: We recommend this to be the default route type in your
              interface - it aims to give practical routes that balance speed
              and pleasantness, suitable for most riders.
            - fastest: This route type will tend to favour busier roads that
              suit more confident riders.
            - quietest: The route type will produce more pleasant, but often
              less direct, routes.  
            - shortest: In general we do not recommend including this in your
              interface unless you have a need for it, as this will not give
              particularly practical routes. These will be literally the
              shortest route, with only land ownership rights causing any
              deviation from this. It will suggest, for instance, dismounting
              and walking down the opposite direction of a one-way street, and
              will gladly route over the top of a hill when that is the shortest
              distance.

    speed : int, defaults to 20 
        The maximum speed at which you will ride. Defaults to 20 km/h. The three
        permitted speeds are 16, 20, and 24 km/h, which correspond roughly to
        10, 12, and 15 miles per hour.

    Returns
    -------
    geopandas.GeoSeries
        GeoSeries with cycling routes
    
    See Also
    --------
    ~stplanpy.cycle.read_key
    
    Examples
    --------
    .. code-block:: python

        import pandas as pd
        import geopandas as gpd
        from shapely import wkt
        from stplanpy import cycle

        # Define two origin-destination lines
        df = pd.DataFrame(
            {"geometry": [
            "LINESTRING(-11785727.431 4453819.337, -11782276.436 4448452.023)", 
            "LINESTRING(-11785787.392 4450797.573, -11787086.209 4449884.472)"]})

        # Convert to WTK
        df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:6933")

        # Read the Cycle Streets API key
        cyclestreets_key = cycle.read_key()

        # Compute routes
        gdf["geometry"] = gdf.routes(api_key=cyclestreets_key)
    """
    if (api_key == None):
        raise Exception("Please provide an API key")

# Ignore shapely warning while using version 1.8
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

# Base url
    base_url = "https://www.cyclestreets.net/api/journey.json?"
    base_url += "&key=%s" % api_key
    base_url += "&plan=%s" % plan
    base_url += "&speed=%s" % speed
    base_url += "&segments=0"
    base_url += "&reporterrors=1"
    base_url += "&redirect=0"

    def routes(x):
# Extract begin and end longitude and latitude of each geometry
        x0 = Point(x.coords[0]).x
        y0 = Point(x.coords[0]).y
        x1 = Point(x.coords[-1]).x
        y1 = Point(x.coords[-1]).y

# Combine into query        
        itinerarypoints = "".join([str(x0), ",", str(y0), "|", str(x1), ",", str(y1)]) 
        url = base_url
        url += "&itinerarypoints=%s" % itinerarypoints

# Retrieve result
        session = CachedSession('cyclestreets_cache', expire_after=timedelta(days=180))
        retry = Retry(connect=3, backoff_factor=0.25)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        req = session.get(url)
        jsn = req.json()

# Convert json into coordinates
        if "marker" in jsn:
            coordinates = jsn["marker"]["@attributes"]["coordinates"]
            coordinates = re.findall(r'[^,\s]+', coordinates)
            coordinates = list(map(float, coordinates))
            elem = iter(coordinates)
            coordinates = [*zip(elem, elem)]
            return LineString(coordinates)
        else:
            if (x0 == x1):
                return LineString([(x0,y0), (x1,y1)])   
            else:
                warnings.warn("No route found. Please relocate one of the \
centroids closer to a road using the corr_cent function in the geo module. \
The tazce codes of the centroids can be found with find_cent function in this \
module.", Warning, stacklevel=2)
                return Point(x0,y0)

    return gpd.GeoSeries(fd[geom].to_crs("EPSG:4326").apply(lambda x: routes(x)), crs="EPSG:4326").to_crs(fd.crs)

def read_key(key_file="cyclestreets_key.txt"):
    r"""
    Read a Cycle Streets API key from a file.

    This function reads the Cycle Streets API key from a file. The default file
    name is "cyclestreets_key.txt" and the key should be stored in plain text.

    Parameters
    ----------
    key_file : str, defaults to "cyclestreets_key.txt"
        Name and path of the file storing the Cycle Streets API key
    
    Returns
    -------
    str
        Cycle Streets API key
    
    See Also
    --------
    ~stplanpy.cycle.routes
    
    Examples
    --------
    .. code-block:: python

        from stplanpy import cycle

        # Read the Cycle Streets API key
        cyclestreets_key = cycle.read_key()
    """
# Read the cyclestreets api key
    with open(key_file) as file:
        for line in file.readlines():
            key = str(line).strip()

    return key

@pf.register_dataframe_method
def find_cent(fd: gpd.GeoDataFrame, orig="orig_taz", dest="dest_taz"):
    r"""
    Find centroid tazce codes

    If the  :func:`~stplanpy.cycle.routes` function is not able to find a route
    between two locations it returns a "Point" geometry. This function can be
    used to find these points and writes the tazce codes of the origin and
    destination to screen. 
    
    Parameters
    ----------
    orig : str, defaults to "orig_taz"
        Column name that contains origin tazce codes.
    dest : str, defaults to "dest_taz"
        Column name that contains destination tazce codes.
 
    Returns
    -------
    None
    
    See Also
    --------
    ~stplanpy.cycle.routes
    
    Examples
    --------
    .. code-block:: python

        import pandas as pd
        import geopandas as gpd
        from shapely import wkt
        from stplanpy import cycle

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

        # Read the Cycle Streets API key
        cyclestreets_key = cycle.read_key()

        # Compute routes
        gdf["geometry"] = gdf.routes(api_key=cyclestreets_key)
        gdf.find_cent()

    """
# Find rows with Point geometry type    
    fd = fd.loc[fd.geom_type == "Point"]

# Print the origin and destination tazce values
    if not fd.empty:
        print(fd[[orig, dest]])
      
    return None
