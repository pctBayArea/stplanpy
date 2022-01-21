r"""
The helper functions in this module print different statistics to screen. These
can be used as input for, for example, the health economic assessment tool
(HEAT) for walking and for cycling [2]_.
"""
import geopandas as gpd
import pandas_flavor as pf

@pf.register_dataframe_method
def mode_stats(fd: gpd.GeoDataFrame, modes=["walk", "bike", "sov"]):
    r"""
    Print mode statistics

    This function prints mode share and number of workers to screen for the
    modes of transportation given in `modes`. The default modes are "walk",
    "bike", and "sov". The whole GeoDataFrame is used to compute the daily
    kilometers. To limit the scope of the calculation one can use the
    :func:`~stplanpy.od.to`, :func:`~stplanpy.od.frm`, and
    :func:`~stplanpy.od.to_frm` functions.

    Parameters
    ----------
    modes : list of str, defaults to ["walk", "bike", "sov"]
        Default list of modes of transportation to show the mode share for.
        Defaults to ["walk", "bike", "sov"].

    See Also
    --------
    ~stplanpy.stats.mode_km
    
    Examples
    --------
    The example data files: "`od_data.csv`_", "`tl_2011_06_taz10.zip`_", and
    "`tl_2020_06_place.zip`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs
        from stplanpy import geo
        from stplanpy import od
        from stplanpy import stats

        # Read origin-destination flow data
        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs()

        # San Francisco Bay Area counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read taz data
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Place code East Palo Alto
        places = ["20956"]

        # Read place data
        place = geo.read_shp("tl_2020_06_place.zip")

        # Keep only East Palo Alto
        place = place[place["placefp"].isin(places)]

        # Compute which taz lay inside a place and which part
        taz = taz.in_place(place)

        # Add county and place codes to data frame.
        flow_data = flow_data.orig_dest(taz)

        # Select origin-destination data to East Palo Alto
        flow_data = flow_data.to("20956")
        
        # Show mode statistics
        flow_data.mode_stats()
    
    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
    """
    al = fd["all"].sum()

    for mode in modes:
        sm = fd[mode].sum()
        ms = sm/al
        print("{:>12} mode share: {:>6.2%} ({:>8.0f} workers)".format(
            mode.capitalize(), ms, sm))

    print("  Total trips per day: " + str(int(2*al)))
    print("")

@pf.register_dataframe_method
def mode_km(fd: gpd.GeoDataFrame, modes=["walk", "bike", "sov"]):
    r"""
    Print daily kilometers per mode

    This function prints both total daily kilometers per mode and daily
    kilometers per mode per person to screen for the modes of transportation
    given in `modes`. The default modes are "walk", "bike", and "sov". The whole
    GeoDataFrame is used to compute the daily kilometers. To limit the scope of the
    calculation one can use the :func:`~stplanpy.od.to`,
    :func:`~stplanpy.od.frm`, and :func:`~stplanpy.od.to_frm` functions.

    Parameters
    ----------
    modes : list of str, defaults to ["walk", "bike", "sov"]
        Default list of modes of transportation to show the mode share for.
        Defaults to ["walk", "bike", "sov"].

    See Also
    --------
    ~stplanpy.stats.mode_stats
    
    Examples
    --------
    The example data files: "`od_data.csv`_", "`tl_2011_06_taz10.zip`_", and
    "`tl_2020_06_place.zip`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs
        from stplanpy import geo
        from stplanpy import od
        from stplanpy import stats

        # Read origin-destination flow data
        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs()

        # San Francisco Bay Area counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read taz data
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Compute centroids
        taz_cent = taz.cent()

        # Place code East Palo Alto
        places = ["20956"]

        # Read place data
        place = geo.read_shp("tl_2020_06_place.zip")

        # Keep only East Palo Alto
        place = place[place["placefp"].isin(places)]

        # Compute which taz lay inside a place and which part
        taz = taz.in_place(place)

        # Add county and place codes to data frame.
        flow_data = flow_data.orig_dest(taz)

        # Select origin-destination data to East Palo Alto
        flow_data = flow_data.to("20956")
        
        # Compute origin-destination lines, and distances
        flow_data["geometry"] = flow_data.od_lines(taz_cent)
        flow_data["distance"] = flow_data.distances()
        
        # Show kilometers per mode statistics
        flow_data.mode_km()
    
    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
    """
    for mode in modes:
        pp = fd[mode].sum()
        km = 2*(fd["distance"] * fd[mode]).sum()/1000
        print("{:>12.2f} km traveled by mode {:<11} per day ({:>6.2f} km pp).".format(km, mode.capitalize(), km/pp))

    print("")

@pf.register_dataframe_method
def carpool(fd: gpd.GeoDataFrame):
    r"""
    Print how may people carpool

    This function prints how many people carpool or drive a single occupancy
    vehicle (SOV). The whole GeoDataFrame is used to compute these numbers.
    To limit the scope of the calculation one can use the
    :func:`~stplanpy.od.to`, :func:`~stplanpy.od.frm`, and
    :func:`~stplanpy.od.to_frm` functions. If the
    :func:`~stplanpy.acs.clean_acs` function is used, set reduced=False.

    See Also
    --------
    ~stplanpy.stats.occupancy
    
    Examples
    --------
    The example data files: "`od_data.csv`_", "`tl_2011_06_taz10.zip`_", and
    "`tl_2020_06_place.zip`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs
        from stplanpy import geo
        from stplanpy import od
        from stplanpy import stats

        # Read origin-destination flow data
        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs(reduced=False)

        # San Francisco Bay Area counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read taz data
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Place code East Palo Alto
        places = ["20956"]

        # Read place data
        place = geo.read_shp("tl_2020_06_place.zip")

        # Keep only East Palo Alto
        place = place[place["placefp"].isin(places)]

        # Compute which taz lay inside a place and which part
        taz = taz.in_place(place)

        # Add county and place codes to data frame.
        flow_data = flow_data.orig_dest(taz)

        # Select origin-destination data to East Palo Alto
        flow_data = flow_data.to("20956")
        
        # Show carpool statistics
        flow_data.carpool()
    
    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
    """
# Check whether carpool columns exist
    if "car_2p" not in fd.columns:
        raise Exception("There is no carpool information in the DataFrame. Please set reduced=True in the \"clean_acs\" function")

# Calculate workers per mode
    sov    = fd["sov"].sum()
    car_2p = fd["car_2p"].sum()
    car_3p = fd["car_3p"].sum()
    car_4p = fd["car_4p"].sum()
    car_5p = fd["car_5p"].sum()
    car_7p = fd["car_7p"].sum()

    total = sov + car_2p + car_3p + car_4p + car_5p + car_7p

    print ("{:>7.0f} people traveled by car, truck, or van".format(total))
    print ("{:>7.0f} people drove alone                         ({:>6.2%})".format(   sov,    sov/total))
    print ("{:>7.0f} people drove in a 2-person carpool         ({:>6.2%})".format(car_2p, car_2p/total))
    print ("{:>7.0f} people drove in a 3-person carpool         ({:>6.2%})".format(car_3p, car_3p/total))
    print ("{:>7.0f} people drove in a 4-person carpool         ({:>6.2%})".format(car_4p, car_4p/total))
    print ("{:>7.0f} people drove in a 5-or-6-person carpool    ({:>6.2%})".format(car_5p, car_5p/total))
    print ("{:>7.0f} people drove in a 7-or-more-person carpool ({:>6.2%})".format(car_7p, car_7p/total))
    print("")

@pf.register_dataframe_method
def occupancy(fd: gpd.GeoDataFrame):
    r"""
    Print average vehicle occupancy rate

    This function prints the average vehicle occupancy rate. For "Car, truck, or
    van -- In a 5-or-6-person carpool" an occupancy of 5.5 is assumed and for
    "Car, truck, or van -- In a 7-or-more-person carpool" an occupancy of 7. The
    whole DataFrame is used to compute this number. To limit the scope of the
    calculation one can use the :func:`~stplanpy.od.to`,
    :func:`~stplanpy.od.frm`, and :func:`~stplanpy.od.to_frm` functions. If the
    :func:`~stplanpy.acs.clean_acs` function is used, set reduced=False.

    See Also
    --------
    ~stplanpy.stats.carpool
    
    Examples
    --------
    The example data files: "`od_data.csv`_", "`tl_2011_06_taz10.zip`_", and
    "`tl_2020_06_place.zip`_", can be downloaded from github.

    .. code-block:: python

        from stplanpy import acs
        from stplanpy import geo
        from stplanpy import od
        from stplanpy import stats

        # Read origin-destination flow data
        flow_data = acs.read_acs("od_data.csv")
        flow_data = flow_data.clean_acs(reduced=False)

        # San Francisco Bay Area counties
        counties = ["001", "013", "041", "055", "075", "081", "085", "095", "097"]

        # Read taz data
        taz = geo.read_shp("tl_2011_06_taz10.zip")

        # Rename columns for consistency
        taz.rename(columns = {"countyfp10":"countyfp", "tazce10":"tazce"}, inplace = True)

        # Filter on county codes
        taz = taz[taz["countyfp"].isin(counties)]

        # Place code East Palo Alto
        places = ["20956"]

        # Read place data
        place = geo.read_shp("tl_2020_06_place.zip")

        # Keep only East Palo Alto
        place = place[place["placefp"].isin(places)]

        # Compute which taz lay inside a place and which part
        taz = taz.in_place(place)

        # Add county and place codes to data frame.
        flow_data = flow_data.orig_dest(taz)

        # Select origin-destination data to East Palo Alto
        flow_data = flow_data.to("20956")
        
        # Show average vehicle occupancy
        flow_data.occupancy()

    References
    ----------
    .. [2] Sonja Kahlmeier, Thomas Gőtschi, Nick Cavill, et al., "Health economic
        assessment tool (HEAT) for walking and for cycling.", World Health
        Organization, Regional Office for Europe, 2017,
        url:`https://www.heatwalkingcycling.org`_

    .. _od_data.csv: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/od_data.csv
    .. _tl_2011_06_taz10.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2011_06_taz10.zip
    .. _tl_2020_06_place.zip: https://raw.githubusercontent.com/pctBayArea/stplanpy/main/examples/tl_2020_06_place.zip
    .. _https://www.heatwalkingcycling.org: https://www.heatwalkingcycling.org
    """
# Check whether carpool columns exist
    if "car_2p" not in fd.columns:
        raise Exception("There is no carpool information in the DataFrame. Please set reduced=True in the \"clean_acs\" function")

# Calculate vehicles         
    sov    = fd["sov"].sum()
    car_2p = fd["car_2p"].sum()/2
    car_3p = fd["car_3p"].sum()/3
    car_4p = fd["car_4p"].sum()/4
    car_5p = fd["car_5p"].sum()/5.5
    car_7p = fd["car_7p"].sum()/7

    vehicles = sov + car_2p + car_3p + car_4p + car_5p + car_7p

# Calculate occupants
    sov    = fd["sov"].sum()
    car_2p = fd["car_2p"].sum()
    car_3p = fd["car_3p"].sum()
    car_4p = fd["car_4p"].sum()
    car_5p = fd["car_5p"].sum()
    car_7p = fd["car_7p"].sum()

    occup = sov + car_2p + car_3p + car_4p + car_5p + car_7p
    
    print("Average vehicle (car, truck, or van) occupancy rate: {:.2f}".format(occup/vehicles))
    print("")
