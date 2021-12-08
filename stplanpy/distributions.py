r"""
The functions in this module can be used to apply different distributions to
flow data.
"""

import numpy as np
import pandas as pd
import pandas_flavor as pf

@pf.register_dataframe_method
def go_dutch(fd: pd.DataFrame, column_names=["all", "distance", "gradient"]) -> pd.DataFrame:
    r"""
    Apply the "go Dutch" scenario.

    This function returns the total number of expected bicyclists under the "go
    Dutch" scenario, :math:`\text{fd["all"]} \cdot p_{\text{cycle}}`. Under this
    scenario people cycle as much as people in Netherlands, taking into account
    differences in the distribution of hilliness and trip distances.
    :math:`\text{fd["all"]}` is the total number of people traveling between an
    origin and a destination using all modes of transportation.
    :math:`p_{\text{cycle}}` is the proportion of expected cyclists and is
    defined as [1]_:

    .. math:: \text{logit}(p_{\text{cycle}}) = - 1.436 - 6.7256 \cdot 10^{-4} d
        + 0.05901 \sqrt{d} + 8.05 \cdot 10^{-9} d^2 - 27.10 \nabla + 9.394 \cdot
        10^{-4} d \; \nabla - 0.1624 \sqrt{d} \; \nabla

    where :math:`d` is the distance in meters and :math:`\nabla` is the
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
    pandas.DataFrame
        Dataframe with the total number of expected bicyclists under the "go
        Dutch" scenario.
    
    See Also
    --------
    ~stplanpy.od.od_lines
    ~stplanpy.od.distances
    ~stplanpy.od.gradient
    
    Examples
    --------
    The example data file, "`od_data.csv`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import distributions

        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs()


    References
    ----------
    .. [1] Robin Lovelace, Anna Goodman, Rachel Aldred, et al., "The Propensity
        to Cycle Tool: An open source online system for sustainable transport
        planning", Journal of transport and land use, vol 10, no 1, pp 505-528,
        2017, url:`https://www.jstor.org/stable/26211742`_ 



    .. _https://www.jstor.org/stable/26211742: https://www.jstor.org/stable/26211742
    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv

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
                - (0.5963 + 0.07626) * distance 
                + 1.866 * np.sqrt(distance)
                + 0.008050 * np.power(distance, 2)
                - 0.2710 * gradient 
                + 0.009394 * distance * gradient
                - 0.05135 * np.sqrt(distance) * gradient)

            return al * np.exp(logit) / (1.0 + np.exp(logit))

    return fd[column_names].apply(lambda x: dutch(*x), axis=1)
