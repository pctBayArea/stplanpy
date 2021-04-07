r"""
The functions in this module can be used to import American community survey
(ACS) 2011-2015 origin destination data into Pandas.
"""

import numpy as np
import pandas as pd

def read_acs(file_name):
    r"""
    Import ACS origin destination data

    This function imports ACS 2011-2015 origin destination (OD) data into a
    Pandas dataframe. In the output dataframe there is one row per origin
    destination pair. The column names and their ACS definitions are shown in
    the table below. For each column name there is an additional column with the
    margin of error. E.g. in addition to "all" there is a column "all_error".

    +--------------+-----------------------------------------------------+
    | Column Name  | ACS description                                     |
    +==============+=====================================================+
    | orig_taz     | RESIDENCE                                           |
    +--------------+-----------------------------------------------------+
    | dest_taz     | WORKPLACE                                           |
    +--------------+-----------------------------------------------------+
    | all          | Total, means of transportation                      |
    +--------------+-----------------------------------------------------+
    | sov          | Car, truck, or van -- Drove alone                   |
    +--------------+-----------------------------------------------------+
    | car_2p       | Car, truck, or van -- In a 2-person carpool         |
    +--------------+-----------------------------------------------------+
    | car_3p       | Car, truck, or van -- In a 3-person carpool         |
    +--------------+-----------------------------------------------------+
    | car_4p       | Car, truck, or van -- In a 4-person carpool         |
    +--------------+-----------------------------------------------------+
    | car_5p       | Car, truck, or van -- In a 5-or-6-person carpool    |
    +--------------+-----------------------------------------------------+
    | car_7p       | Car, truck, or van -- In a 7-or-more-person carpool |
    +--------------+-----------------------------------------------------+
    | bus          | Bus or trolley bus                                  |
    +--------------+-----------------------------------------------------+
    | streetcar    | Streetcar or trolley car                            |
    +--------------+-----------------------------------------------------+
    | subway       | Subway or elevated                                  |
    +--------------+-----------------------------------------------------+
    | railroad     | Railroad                                            |
    +--------------+-----------------------------------------------------+
    | ferry        | Ferryboat                                           |
    +--------------+-----------------------------------------------------+
    | bike         | Bicycle                                             |
    +--------------+-----------------------------------------------------+
    | walk         | Walked                                              |
    +--------------+-----------------------------------------------------+
    | taxi         | Taxicab                                             |
    +--------------+-----------------------------------------------------+
    | motorcycle   | Motorcycle                                          |
    +--------------+-----------------------------------------------------+
    | other        | Other method                                        |
    +--------------+-----------------------------------------------------+
    | home         | Worked at home                                      |
    +--------------+-----------------------------------------------------+
    | auto         | Auto                                                |
    +--------------+-----------------------------------------------------+
    
    The origin destination flow data can be found on the `website`_ of the
    American Association of State Highway and Transportation Officials (AASHTO)
    through their Census Transportation Planning Products Program (CTPP).

    .. _website: https://ctpp.transportation.org/2012-2016-5-year-ctpp/

    Parameters
    ----------
    file_name : str
        File_name is the name and path of an ACS csv file

    Returns
    -------
    pandas.DataFrame
        Dataframe with origin destination data broken down by mode
    
    See Also
    --------
    ~stplanpy.acs.clean_acs
    
    Examples
    --------
    The example data file, "`od_data.csv`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs

        flow_data = acs.read_acs("od_data.csv")


    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv

    """

# Column names in output data frame
    column_names = [
        "orig_taz", "dest_taz", 
        "all", "all_error", 
        "sov", "sov_error", 
        "car_2p", "car_2p_error", 
        "car_3p", "car_3p_error", 
        "car_4p", "car_4p_error", 
        "car_5p", "car_5p_error", 
        "car_7p", "car_7p_error", 
        "bus", "bus_error", 
        "streetcar", "streetcar_error", 
        "subway", "subway_error",  
        "railroad", "railroad_error",  
        "ferry", "ferry_error", 
        "bike", "bike_error", 
        "walk", "walk_error", 
        "taxi", "taxi_error", 
        "motorcycle", "motorcycle_error", 
        "other", "other_error", 
        "home", "home_error", 
        "auto", "auto_error"]

    full_data = pd.DataFrame({"How":  [
            "Total, means of transportation", 
            "Total, means of transportation",  
            "Car, truck, or van -- Drove alone", 
            "Car, truck, or van -- Drove alone",  
            "Car, truck, or van -- In a 2-person carpool", 
            "Car, truck, or van -- In a 2-person carpool",  
            "Car, truck, or van -- In a 3-person carpool",  
            "Car, truck, or van -- In a 3-person carpool",  
            "Car, truck, or van -- In a 4-person carpool",  
            "Car, truck, or van -- In a 4-person carpool",  
            "Car, truck, or van -- In a 5-or-6-person carpool",  
            "Car, truck, or van -- In a 5-or-6-person carpool",  
            "Car, truck, or van -- In a 7-or-more-person carpool",  
            "Car, truck, or van -- In a 7-or-more-person carpool",  
            "Bus or trolley bus",  
            "Bus or trolley bus",  
            "Streetcar or trolley car",  
            "Streetcar or trolley car",  
            "Subway or elevated",  
            "Subway or elevated",  
            "Railroad",  
            "Railroad",  
            "Ferryboat",  
            "Ferryboat",  
            "Bicycle",  
            "Bicycle",  
            "Walked",  
            "Walked",  
            "Taxicab",  
            "Taxicab",  
            "Motorcycle",  
            "Motorcycle",  
            "Other method",  
            "Other method",  
            "Worked at home",  
            "Worked at home",  
            "Auto",  
            "Auto",  
        ], "What": [
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
            "Estimate", "Margin of Error",
        ]})

# Read American Community Survey flow data
    raw_data = pd.read_csv(
        file_name, 
        skiprows=3, skipfooter=3, 
        header=None, engine="python", 
        names=[
            "Origin", "Destination", 
            "How", "What", "Number"])

# indices of start of data frames     
    indices = (raw_data.loc[raw_data["How"].str.contains(
        "Total, means of transportatio") & raw_data[
        "What"].str.contains("Estimate")].index.values)
    
# Set empty array
    np_data = np.zeros((len(indices), len(column_names)))

# Add index of last row
    indices = np.append(indices, raw_data.tail(1).index.values+1, 0)

# Creat one dataframe per origin destination pair and write data to numpy array
    for i, idx0 in np.ndenumerate(indices[:-1]):
        idx1 = indices[i[0]+1]
        rd = raw_data[idx0:idx1]
        np_data[i[0],0] = rd["Origin"].head(1).values[0].split(',')[0].split(' ')[1]
        np_data[i[0],1] = rd["Destination"].head(1).values[0].split(',')[0].split(' ')[1]
        rd = pd.merge(full_data, rd, on=["How", "What"], how="left").fillna(value=0.0)
        np_data[i[0],2:] = rd["Number"].values 

# Convert to dataframe
    fd = pd.DataFrame(data=np_data, columns=column_names)

# Format back to string
    fd["orig_taz"] = fd["orig_taz"].apply("{:0>8.0f}".format)
    fd["dest_taz"] = fd["dest_taz"].apply("{:0>8.0f}".format)

    return fd

import pandas as pd
import pandas_flavor as pf

@pf.register_dataframe_method
def clean_acs(fd: pd.DataFrame, 
        returns=False, 
        groups=True, 
        home=True,
        reduced=True, 
        error=False) -> pd.DataFrame:
    r"""
    
    Test
    """        

#    if "latitude" not in obj.columns or "longitude" not in obj.columns:
#            raise AttributeError("Must have 'latitude' and 'longitude'.")

    if (returns):
# Add return data for commute trips per day
        df = fd.copy()
        df = df[[
            "dest_taz", "orig_taz",
            "all", "all_error",
            "sov", "sov_error",
            "car_2p", "car_2p_error",
            "car_3p", "car_3p_error",
            "car_4p", "car_4p_error",
            "car_5p", "car_5p_error",
            "car_7p", "car_7p_error",
            "bus", "bus_error",
            "streetcar", "streetcar_error",
            "subway", "subway_error",
            "railroad", "railroad_error",
            "ferry", "ferry_error",
            "bike", "bike_error",
            "walk", "walk_error",
            "taxi", "taxi_error",
            "motorcycle", "motorcycle_error",
            "other", "other_error",
            "home", "home_error",
            "auto", "auto_error"]]
        df.rename(columns = {
            "dest_taz":"orig_taz", 
            "orig_taz":"dest_taz"}, inplace = True)
        fd = pd.concat([fd, df], ignore_index=True)

    if (groups):
# Define some groups
        fd["active"] = (
            + fd["walk"]
            + fd["bike"])
        fd["active_error"] = (
            + fd["walk_error"]**2
            + fd["bike_error"]**2)**(1/2)
        fd["transit"] = (
            + fd["bus"]
            + fd["streetcar"]
            + fd["subway"]
            + fd["railroad"]
            + fd["ferry"])
        fd["transit_error"] = (
            + fd["bus_error"]**2
            + fd["streetcar_error"]**2
            + fd["subway_error"]**2
            + fd["railroad_error"]**2
            + fd["ferry_error"]**2)**(1/2)
        fd["carpool"] = (
            + fd["car_2p"]
            + fd["car_3p"]
            + fd["car_4p"]
            + fd["car_5p"]
            + fd["car_7p"])
        fd["carpool_error"] = (
            + fd["car_2p_error"]**2
            + fd["car_3p_error"]**2
            + fd["car_4p_error"]**2
            + fd["car_5p_error"]**2
            + fd["car_7p_error"]**2)**(1/2)

    if (home):
# People working from home do not travel
        fd["all"] = fd["all"] - fd["home"]
    
    if (reduced and groups):
# Columns to keep
        fd = fd[[
            "orig_taz",
            "dest_taz",
            "all",
            "all_error",
            "home",
            "home_error",
            "walk",
            "walk_error",
            "bike",
            "bike_error",
            "sov",
            "sov_error",
            "active",
            "active_error",
            "transit",
            "transit_error",
            "carpool",
            "carpool_error"]]
    elif (reduced and not groups):
# Columns to keep
        fd = fd[[
            "orig_taz",
            "dest_taz",
            "all",
            "all_error",
            "home",
            "home_error",
            "walk",
            "walk_error",
            "bike",
            "bike_error",
            "sov",
            "sov_error"]]

    if not (error):
        fd = fd[fd.columns.drop(list(fd.filter(regex="_error")))]

# Fix index
    fd = fd.reset_index(drop=True)

    return fd
