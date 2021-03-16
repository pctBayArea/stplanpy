#!/usr/bin/python3

import pandas as pd
import pandas_flavor as pf

@pf.register_dataframe_method
def clean_acs(fd: pd.DataFrame, 
        returns=False, 
        groups=True, 
        home=True,
        reduced=True, 
        error=False) -> pd.DataFrame:

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
