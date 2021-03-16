#!/usr/bin/python3

import numpy as np
import pandas as pd
#pandas-flavor 0.2.0

def read_acs(file_name):

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
    df = pd.DataFrame(data=np_data, columns=column_names)

# Format back to string
    df["orig_taz"] = df["orig_taz"].apply("{:0>8.0f}".format)
    df["dest_taz"] = df["dest_taz"].apply("{:0>8.0f}".format)

    return df
