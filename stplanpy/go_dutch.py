#!/usr/bin/python3

import numpy as np
#import pandas_flavor as pf

def go_dutch(flow_data):

    def dist_func(distance, gradient):

        distance /= 1000

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

            return np.exp(logit) / (1.0 + np.exp(logit))

    return flow_data.apply(lambda x: x["all"] * dist_func(x["distance"], x["gradient"]), axis=1)
