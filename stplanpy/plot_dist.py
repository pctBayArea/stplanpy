#!/usr/bin/python3

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_dist(flow_data, out_dir):

# Convert meters to kilometers and make histogram
    hist_all, bins = np.histogram(flow_data["distance"]/1000, weights=flow_data["all"], bins=np.linspace(0,100,201))
    density = 1.0/(sum(hist_all)*np.diff(bins))
    widths = np.diff(bins)
    hist_all *= density             
    plt.figure(0)
    plt.bar(bins[:-1], hist_all, widths, align="edge")
    plt.title("Distribution of trips as function of distance traveled")
    plt.xlabel("Distance (km)")
    plt.ylabel("Fraction of trips")
    plt.savefig(out_dir + "/dist_all.png")
    plt.close(0)

    hist_all, bins = np.histogram(flow_data["distance"]/1000, weights=flow_data["all"], bins=np.linspace(0,100,201))
    widths = np.diff(bins)
    hist_all *= density
    hist_all = np.cumsum(hist_all * np.diff(bins))
    plt.figure(1)             
    plt.bar(bins[:-1], hist_all, widths, align="edge")
    plt.title("Cumulative number of trips as function of distance traveled")
    plt.xlabel("Distance (km)")
    plt.ylabel("Fraction of trips")
    plt.savefig(out_dir + "/cum_all.png")
    plt.close(1)

    hist_bike, bins = np.histogram(flow_data["distance"]/1000, weights=flow_data["bike"], bins=np.linspace(0,100,201))
    widths = np.diff(bins)
    hist_bike *= density             
    plt.figure(2)             
    plt.bar(bins[0:80], hist_bike[0:80], widths[0:80], align="edge")
    plt.title("Distribution of trips by bicycle as function of distance traveled \n (normalized by all trips)")
    plt.xlabel("Distance (km)")
    plt.ylabel("Fraction of trips")
    plt.savefig(out_dir + "/dist_bike.png")
    plt.close(2)

    hist_bike, bins = np.histogram(flow_data["distance"]/1000, weights=flow_data["bike"], bins=np.linspace(0,100,201))
    widths = np.diff(bins)
    hist_bike *= density             
    hist_bike = np.cumsum(hist_bike * np.diff(bins))
    plt.figure(3)             
    plt.bar(bins[0:80], hist_bike[0:80], widths[0:80], align="edge")
    plt.title("Cumulative number of trips by bicycle as function of distance traveled \n (normalized by all trips)")
    plt.xlabel("Distance (km)")
    plt.ylabel("Fraction of trips")
    plt.savefig(out_dir + "/cum_bike.png")
    plt.close(3)

    hist_go_dutch, bins = np.histogram(flow_data["distance"]/1000, weights=flow_data["go_dutch"], bins=np.linspace(0,100,201))
    widths = np.diff(bins)
    hist_go_dutch *= density             
    plt.figure(4)             
    plt.bar(bins[0:80], hist_go_dutch[0:80], widths[0:80], align="edge")
    plt.title("Distribution of trips by bicycle as function of distance traveled \n (normalized by all trips) (go Dutch)")
    plt.xlabel("Distance (km)")
    plt.ylabel("Fraction of trips")
    plt.savefig(out_dir + "/dist_go_dutch.png")
    plt.close(4)

    hist_go_dutch, bins = np.histogram(flow_data["distance"]/1000, weights=flow_data["go_dutch"], bins=np.linspace(0,100,201))
    widths = np.diff(bins)
    hist_go_dutch *= density             
    hist_go_dutch = np.cumsum(hist_go_dutch * np.diff(bins))
    plt.figure(5)             
    plt.bar(bins[0:80], hist_go_dutch[0:80], widths[0:80], align="edge")
    plt.title("Cumulative number of trips by bicycle as function of distance traveled \n (normalized by all trips) (go Dutch)")
    plt.xlabel("Distance (km)")
    plt.ylabel("Fraction of trips")
    plt.savefig(out_dir + "/cum_go_dutch.png")
    plt.close(5)
