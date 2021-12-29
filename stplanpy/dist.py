r"""
The functions in this module can be used to apply different distributions to
flow data.
"""

import numpy as np
import pandas as pd
import pandas_flavor as pf

@pf.register_dataframe_method
def ebike(fd: pd.DataFrame, column_names=["all", "distance", "gradient"]) -> pd.Series:
    r"""
    Apply the "e-bike" scenario.

    This function returns the total number of expected bicyclists under the
    "e-bike" scenario. Under this scenario all people aquire e-bikes and ride
    them as much as people in Netherlands do, taking into account both hilliness
    and trip distance. The total number of expected bicyclists is equal to:
    :math:`\text{fd["all"]} \cdot p_{\text{cycle}}`, where
    :math:`\text{fd["all"]}` is the total number of people traveling between an
    origin and a destination using all modes of transportation, and
    :math:`p_{\text{cycle}}` is the proportion of expected cyclists [1]_:

    .. math:: \text{logit}(p_{\text{cycle}}) = - 1.436 + 0.05901 \sqrt{d} 
        - 6.1546 \cdot 10^{-4} d + 7.9413 \cdot 10^{-9} d^2 - 8.98 \nabla 
        - 0.1624 \sqrt{d} \; \nabla + 9.394 \cdot 10^{-4} d \; \nabla 

    Here :math:`d` is the distance in meters and :math:`\nabla` is the
    gradient :math:`h/d`, with :math:`h` the elevation difference in meters
    between the origin and the destination. Only distances smaller than 30 km
    are considered.
    
    Parameters
    ----------
    column_names : list of str, defaults to ["all", "distance", "gradient"]
        Names of the input columns that this function operates on. The "all"
        column contains the total number of people traveling between an origin
        and a destination using all modes of transportation, the "distance"
        column contains the distance between the origin and the destination, and
        the "gradient" column contains the gradient as defined above. 
    
    Returns
    -------
    pandas.Series
        Series with the total number of expected bicyclists under the "e-bike"
        scenario.
    
    See Also
    --------
    ~stplanpy.dist.go_dutch
    ~stplanpy.od.od_lines
    ~stplanpy.od.distances
    ~stplanpy.od.gradient
    
    Examples
    --------
    .. code-block:: python

        import pandas as pd
        import geopandas as gpd
        from shapely import wkt
        from stplanpy import od
        from stplanpy import dist

        # Define two origin-destination lines
        df = pd.DataFrame({
            "all": [5, 10],
            "geometry": [
            "LINESTRING(-11785727.431 4453819.337, -11782276.436 4448452.023)",
            "LINESTRING(-11785787.392 4450797.573, -11787086.209 4449884.472)"]})

        # Convert to WTK
        df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:6933")

        # compute distances and set gradient to zero
        gdf["distance"] = gdf.distances()
        gdf["gradient"] = 0.0

        # Compute e-bike scenario
        gdf["ebike"] = gdf.ebike()

    .. _https://www.jstor.org/stable/26211742: https://www.jstor.org/stable/26211742
    """

    def ebikes(*x):
        al = x[0]
        distance = x[1] / 1000 # to km
        gradient = x[2] * 100 # to %

        if (distance > 30):
# Negligeble cycling past 30km            
            return 0.0
        else:
            logit = (- 3.959 + 2.523 
                + 1.866 * np.sqrt(distance) 
                + (0.05710 - 0.5963 - 0.07626) * distance
                + (0.008050 - 0.0001087) * np.power(distance, 2)
                + (0.1812-0.2710) * gradient
                - 0.05135 * np.sqrt(distance) * gradient
                + 0.009394 * distance*gradient) 

            return al * np.exp(logit) / (1.0 + np.exp(logit))

    return fd[column_names].apply(lambda x: ebikes(*x), axis=1)

@pf.register_dataframe_method
def go_dutch(fd: pd.DataFrame, column_names=["all", "distance", "gradient"]) -> pd.Series:
    r"""
    Apply the "go Dutch" scenario.

    This function returns the total number of expected bicyclists under the "go
    Dutch" scenario. Under this scenario people cycle as much as people in
    Netherlands do, taking into account both hilliness and trip distance. The total
    number of expected bicyclists is equal to: :math:`\text{fd["all"]} \cdot
    p_{\text{cycle}}`, where :math:`\text{fd["all"]}` is the total number of
    people traveling between an origin and a destination using all modes of
    transportation, and :math:`p_{\text{cycle}}` is the proportion of expected
    cyclists [1]_:

    .. math:: \text{logit}(p_{\text{cycle}}) = - 1.436 + 0.05901 \sqrt{d} 
        - 6.7256 \cdot 10^{-4} d + 8.05 \cdot 10^{-9} d^2 - 27.10 \nabla 
        - 0.1624 \sqrt{d} \; \nabla + 9.394 \cdot 10^{-4} d \; \nabla 

    Here :math:`d` is the distance in meters and :math:`\nabla` is the
    gradient :math:`h/d`, with :math:`h` the elevation difference in meters
    between the origin and the destination. Only distances smaller than 30 km
    are considered.
    
    Parameters
    ----------
    column_names : list of str, defaults to ["all", "distance", "gradient"]
        Names of the input columns that this function operates on. The "all"
        column contains the total number of people traveling between an origin
        and a destination using all modes of transportation, the "distance"
        column contains the distance between the origin and the destination, and
        the "gradient" column contains the gradient as defined above. 
    
    Returns
    -------
    pandas.Series
        Series with the total number of expected bicyclists under the "go Dutch"
        scenario.
    
    See Also
    --------
    ~stplanpy.dist.ebike
    ~stplanpy.od.od_lines
    ~stplanpy.od.distances
    ~stplanpy.od.gradient
    
    Examples
    --------
    .. code-block:: python

        import pandas as pd
        import geopandas as gpd
        from shapely import wkt
        from stplanpy import od
        from stplanpy import dist

        # Define two origin-destination lines
        df = pd.DataFrame({
            "all": [5, 10],
            "geometry": [
            "LINESTRING(-11785727.431 4453819.337, -11782276.436 4448452.023)",
            "LINESTRING(-11785787.392 4450797.573, -11787086.209 4449884.472)"]})

        # Convert to WTK
        df["geometry"] = gpd.GeoSeries.from_wkt(df["geometry"])

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:6933")

        # compute distances and set gradient to zero
        gdf["distance"] = gdf.distances()
        gdf["gradient"] = 0.0

        # Compute go_dutch scenario
        gdf["go_dutch"] = gdf.go_dutch()

    References
    ----------
    .. [1] Robin Lovelace, Anna Goodman, Rachel Aldred, et al., "The Propensity
        to Cycle Tool: An open source online system for sustainable transport
        planning", Journal of transport and land use, vol 10, no 1, pp 505-528,
        2017, url:`https://www.jstor.org/stable/26211742`_ 

    .. _https://www.jstor.org/stable/26211742: https://www.jstor.org/stable/26211742
    """

    def dutch(*x):
        al = x[0]
        distance = x[1] / 1000 # to km
        gradient = x[2] * 100 # to %

        if (distance > 30):
# Negligeble cycling past 30km            
            return 0.0
        else:
            logit = (
                - 3.959 + 2.523 
                + 1.866 * np.sqrt(distance)
                - (0.5963 + 0.07626) * distance 
                + 0.008050 * np.power(distance, 2)
                - 0.2710 * gradient 
                - 0.05135 * np.sqrt(distance) * gradient
                + 0.009394 * distance * gradient)

            return al * np.exp(logit) / (1.0 + np.exp(logit))

    return fd[column_names].apply(lambda x: dutch(*x), axis=1)
