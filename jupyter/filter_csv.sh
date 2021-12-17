#!/bin/bash

# Remove old file
rm od_data.csv

# Filter on codes in taz file
for file in `ls /home/arnout/ShinyApps/pct-inputs/01_raw/02_travel_data/commute/taz/acs2012-2016/*antaClaraCount*.csv`;
#    do echo $file;
    do grep -w -F -f taz.txt $file >> od_data.csv;
done 

# Semove duplicates but keep first occurence
awk '!visited[$0]++' od_data.csv > od_data.tmp
mv od_data.tmp od_data.csv

# Find the first file only
firstFile=`ls /home/arnout/ShinyApps/pct-inputs/01_raw/02_travel_data/commute/taz/acs2012-2016/*antaClaraCount*.csv| head -1`

# Add first 3 lines
head -n3 $firstFile| cat - od_data.csv > od_data.tmp && mv od_data.tmp od_data.csv

# Add last 3 lines
tail -n3 $firstFile >> od_data.csv 
