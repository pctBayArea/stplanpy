#!/usr/bin/python3

import numpy as np
import pandas as pd
import geopandas as gpd

def read_acs(file_name):

# Column names in output data frame
    column_names = [
        "orig_code", "dest_code", 
        "all", "all_error", 
        "car_1p", "car_1p_error", 
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
        "bicycle", "bicycle_error", 
        "walked", "walked_error", 
        "taxi", "taxi_error", 
        "motorcycle", "motorcycle_error", 
        "other", "other_error", 
        "home", "home_error", 
        "auto", "auto_error"]

# Read American Community Survey flow data
    raw_data = pd.read_csv(
        file_name, 
        skiprows=3, skipfooter=3, 
        header=None, engine="python", 
        names=[
            "Origin", "Destination", 
            "How", "What", "Number"])

# Count unique columns
    columns = len(raw_data[raw_data["How"].str.contains(
        "Total, means of transportatio") & raw_data[
        "What"].str.contains("Estimate")])

# Set empty array
    np_data = np.zeros((columns, len(column_names)))

# Define dataframe
    df = pd.DataFrame(data=np_data, columns=column_names)

# Iterate over rows of raw dataframe and copy to df
    row_nr = -1
    for index, row in raw_data.iterrows():
        if row["How"] == "Total, means of transportation" \
                and row["What"] == "Estimate":
            row_nr = row_nr + 1
            df.loc[row_nr,"orig_code"] = row[
                "Origin"].split(',')[0].split(' ')[1]
            df.loc[row_nr,"dest_code"] = row[
                "Destination"].split(',')[0].split(' ')[1]
            df.loc[row_nr,"all"] = row["Number"] 
        if row["How"] == "Total, means of transportation" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"all_error"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- Drove alone" \
                and row["What"] == "Estimate":
            df.loc[row_nr,"car_1p"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- Drove alone" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"car_1p_error"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 2-person carpool" \
                and row["What"] == "Estimate":
            df.loc[row_nr,"car_2p"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 2-person carpool" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"car_2p_error"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 3-person carpool" \
                and row["What"] == "Estimate":
            df.loc[row_nr,"car_3p"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 3-person carpool" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"car_3p_error"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 4-person carpool" \
                and row["What"] == "Estimate":
            df.loc[row_nr,"car_4p"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 4-person carpool" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"car_4p_error"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 5-or-6-person carpool" \
                and row["What"] == "Estimate":
            df.loc[row_nr,"car_5p"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 5-or-6-person carpool" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"car_5p_error"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 7-or-more-person carpool" \
                and row["What"] == "Estimate":
            df.loc[row_nr,"car_7p"] = row["Number"] 
        if row["How"] == "Car, truck, or van -- In a 7-or-more-person carpool" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"car_7p_error"] = row["Number"] 
        if row["How"] == "Bus or trolley bus" and row["What"] == "Estimate":
            df.loc[row_nr,"bus"] = row["Number"] 
        if row["How"] == "Bus or trolley bus" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"bus_error"] = row["Number"] 
        if row["How"] == "Streetcar or trolley car" \
                and row["What"] == "Estimate":
            df.loc[row_nr,"streetcar"] = row["Number"] 
        if row["How"] == "Streetcar or trolley car" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"streetcar_error"] = row["Number"] 
        if row["How"] == "Subway or elevated" and row["What"] == "Estimate":
            df.loc[row_nr,"subway"] = row["Number"] 
        if row["How"] == "Subway or elevated" \
                and row["What"] == "Margin of Error":
            df.loc[row_nr,"subway_error"] = row["Number"] 
        if row["How"] == "Railroad" and row["What"] == "Estimate":
            df.loc[row_nr,"railroad"] = row["Number"] 
        if row["How"] == "Railroad" and row["What"] == "Margin of Error":
            df.loc[row_nr,"railroad_error"] = row["Number"] 
        if row["How"] == "Ferryboat" and row["What"] == "Estimate":
            df.loc[row_nr,"ferry"] = row["Number"] 
        if row["How"] == "Ferryboat" and row["What"] == "Margin of Error":
            df.loc[row_nr,"ferry_error"] = row["Number"] 
        if row["How"] == "Bicycle" and row["What"] == "Estimate":
            df.loc[row_nr,"bicycle"] = row["Number"] 
        if row["How"] == "Bicycle" and row["What"] == "Margin of Error":
            df.loc[row_nr,"bicycle_error"] = row["Number"] 
        if row["How"] == "Walked" and row["What"] == "Estimate":
            df.loc[row_nr,"walked"] = row["Number"] 
        if row["How"] == "Walked" and row["What"] == "Margin of Error":
            df.loc[row_nr,"walked_error"] = row["Number"] 
        if row["How"] == "Taxicab" and row["What"] == "Estimate":
            df.loc[row_nr,"taxi"] = row["Number"] 
        if row["How"] == "Taxicab" and row["What"] == "Margin of Error":
            df.loc[row_nr,"taxi_error"] = row["Number"] 
        if row["How"] == "Motorcycle" and row["What"] == "Estimate":
            df.loc[row_nr,"motorcycle"] = row["Number"] 
        if row["How"] == "Motorcycle" and row["What"] == "Margin of Error":
            df.loc[row_nr,"motorcycle_error"] = row["Number"] 
        if row["How"] == "Other method" and row["What"] == "Estimate":
            df.loc[row_nr,"other"] = row["Number"] 
        if row["How"] == "Other method" and row["What"] == "Margin of Error":
            df.loc[row_nr,"other_error"] = row["Number"] 
        if row["How"] == "Worked at home" and row["What"] == "Estimate":
            df.loc[row_nr,"home"] = row["Number"] 
        if row["How"] == "Worked at home" and row["What"] == "Margin of Error":
            df.loc[row_nr,"home_error"] = row["Number"] 
        if row["How"] == "Auto" and row["What"] == "Estimate":
            df.loc[row_nr,"auto"] = row["Number"] 
        if row["How"] == "Auto" and row["What"] == "Margin of Error":
            df.loc[row_nr,"auto_error"] = row["Number"]

    return df
