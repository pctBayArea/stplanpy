r"""
The functions in this module perform various operations on route data from CycleStreet.net
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
def route_lines(fd: gpd.GeoDataFrame, geom="geometry", api_key=None, plan="balanced") -> gpd.GeoDataFrame:
    r"""
    Compute routes
    """
# Ignore shapely warning while using version 1.8
    warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

# Base url
    base_url = "https://www.cyclestreets.net/api/journey.json?"
    base_url += "&key=%s" % api_key
    base_url += "&plan=%s" % plan
    base_url += "&reporterrors=1"

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
    Read cyclestreets API key.
    """
# Read the cyclestreets api key
    with open(key_file) as file:
        for line in file.readlines():
            key = str(line).strip()

    return key

#@pf.register_dataframe_method
#def route_urls(fd: pd.DataFrame, geom="geometry", api_key=None, plan="balanced") -> pd.DataFrame:
#    r"""
#    Compute routes
#    """
#
## Base url
#    base_url = "https://www.cyclestreets.net/api/journey.json?"
#    base_url += "&key=%s" % api_key
#    base_url += "&plan=%s" % plan
#    base_url += "&reporterrors=1"
#
#    def urls(x):
#        x0 = Point(x.coords[0]).x
#        y0 = Point(x.coords[0]).y
#        x1 = Point(x.coords[-1]).x
#        y1 = Point(x.coords[-1]).y
#
## Combine into query        
#        itinerarypoints = "".join([str(x0), ",", str(y0), "|", str(x1), ",", str(y1)]) 
#        url = base_url
#        url += "&itinerarypoints=%s" % itinerarypoints
#
#        return url                                 
#
#    return fd[geom].to_crs("EPSG:4326").apply(lambda x: urls(x))
