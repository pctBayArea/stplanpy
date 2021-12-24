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
def routes(fd: gpd.GeoDataFrame, geom="geometry", api_key=None, plan="balanced",
speed=20, segments=0, reporterrors=1, redirect=0) -> gpd.GeoSeries:
    r"""
    Compute routes
    """
    if (api_key == None ):
        raise AttributeError("Please provide an API key")

# Ignore shapely warning while using version 1.8
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

# Base url
    base_url = "https://www.cyclestreets.net/api/journey.json?"
    base_url += "&key=%s" % api_key
    base_url += "&plan=%s" % plan
    base_url += "&speed=%s" % speed
    base_url += "&segments=%s" % segments
    base_url += "&reporterrors=%s" % reporterrors
    base_url += "&redirect=%s" % redirect

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
            if (segments == 0):
                coordinates = jsn["marker"]["@attributes"]["coordinates"]
            else:
                coordinates = jsn["marker"][0]["@attributes"]["coordinates"]
                
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
The tazce codes of the centrods can be found with find_cent function in the \
geo module.", Warning, stacklevel=2)
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
