# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:26:15 2018

@author: tih
"""

import numpy as np
import time
import sys

def Run(Runoff_in_m3_month, flow_directions, Basin):

    time1 = time.time()

    # Get properties of the raster
    size_X = np.size(Runoff_in_m3_month,2)
    size_Y = np.size(Runoff_in_m3_month,1)

    # input data test
    Runoff_in_m3_month[np.isnan(Runoff_in_m3_month)] = 0
    dataflow_in0 = np.ones([size_Y,size_X])
    dataflow_in = np.zeros([int(np.size(Runoff_in_m3_month,0)+1),size_Y, size_X])
    dataflow_in[0,:,:] = dataflow_in0 * Basin
    dataflow_in[1:,:,:] = Runoff_in_m3_month * Basin

    # The flow directions parameters of HydroSHED
    Directions = [1, 2, 4, 8, 16, 32, 64, 128]

    # Route the data
    dataflow_next = dataflow_in[0,:,:]
    data_flow_tot = np.copy(dataflow_in)
    dataflow_previous = np.zeros([size_Y, size_X])
    while np.sum(dataflow_next) != np.sum(dataflow_previous):
        data_flow_round = np.zeros([int(np.size(Runoff_in_m3_month,0)+1),size_Y, size_X])
        dataflow_previous = np.copy(dataflow_next)
        for Direction in Directions:

            data_dir = np.zeros([int(np.size(Runoff_in_m3_month,0)+1),size_Y, size_X])
            data_dir[:,np.logical_and(flow_directions == Direction,dataflow_next == 1)] = dataflow_in[:,np.logical_and(flow_directions == Direction,dataflow_next == 1)]
            data_flow = np.zeros([int(np.size(Runoff_in_m3_month,0)+1), size_Y, size_X])

            if Direction == 4:
                data_flow[:,1:,:] = data_dir[:,:-1,:]
            if Direction == 2:
                data_flow[:,1:,1:] = data_dir[:,:-1,:-1]
            if Direction == 1:
                data_flow[:,:,1:] = data_dir[:,:,:-1]
            if Direction == 128:
                data_flow[:,:-1,1:] = data_dir[:,1:,:-1]
            if Direction == 64:
                data_flow[:,:-1,:] = data_dir[:,1:,:]
            if Direction == 32:
                data_flow[:,:-1,:-1] = data_dir[:,1:,1:]
            if Direction == 16:
                data_flow[:,:,:-1] = data_dir[:,:,1:]
            if Direction == 8:
                data_flow[:,1:,:-1] = data_dir[:,:-1,1:]

            data_flow_round += data_flow
        dataflow_in = np.copy(data_flow_round)
        dataflow_next[dataflow_in[0,:,:]==0.] = 0

        sys.stdout.write("\rstill %s pixels to go        " %int(np.nansum(dataflow_next)))
        sys.stdout.flush()

        data_flow_tot += data_flow_round

    print 'time', time.time() - time1

    # Seperate the array in a river array and the routed input
    Accumulated_Pixels = data_flow_tot[0,:,:] * Basin
    Routed_Array = data_flow_tot[1:,:,:] * Basin

    # Define the 1% highest pixels as rivers
    Routed_Array_mean = np.nanmean(Routed_Array,axis=0)
    Rivers = np.zeros([np.size(Routed_Array_mean,0),np.size(Routed_Array_mean,1)])
    Routed_Array_mean[Basin != 1] = np.nan
    Routed_Discharge_Ave_number = np.nanpercentile(Routed_Array_mean,98)
    Rivers[Routed_Array_mean > Routed_Discharge_Ave_number] = 1  # if yearly average is larger than the 99 percentile than it is defined as a river
    Routed_Array[:, Basin != 1] = -9999

    return(Routed_Array, Accumulated_Pixels, Rivers)
