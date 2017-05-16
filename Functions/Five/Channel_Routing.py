# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:47:16 2017

@author: tih
"""


import time
import numpy as np
import pandas as pd

from wa.General import raster_conversions as RC

def Channel_Routing(Name_NC_DEM_Dir, Name_NC_Runoff, Name_NC_Basin, Reference_data, Degrees = 0):
    		
    time1 = time.time()

    # Extract runoff data from NetCDF file
    Runoff = RC.Open_nc_array(Name_NC_Runoff)

    # Extract flow direction data from NetCDF file
    flow_directions = RC.Open_nc_array(Name_NC_DEM_Dir)
    
    # Extract basin data from NetCDF file	
    Basin = RC.Open_nc_array(Name_NC_Basin)	 				
			
    if Degrees != 0:
	   
        import wa.Functions.Start.Area_converter as AC				
        # Convert area from degrees to m2									
        Areas_in_m2 = AC.Degrees_to_m2(Reference_data)
        Runoff_in_m3_month = ((Runoff/1000) * Areas_in_m2)
    else:
        Runoff_in_m3_month = Runoff

    # Get properties of the raster
    size_X = np.size(Runoff,2)
    size_Y = np.size(Runoff,1)	

    # input data test
    dataflow_in0 = np.ones([size_Y,size_X])
    dataflow_in = np.zeros([int(np.size(Runoff_in_m3_month,0)+1),size_Y, size_X])
    dataflow_in[0,:,:] = dataflow_in0 * Basin
    dataflow_in[1:,:,:] = Runoff_in_m3_month * Basin

    # The flow directions parameters of HydroSHED
    Directions = [1, 2, 4, 8, 16, 32, 64, 128]

    # Route the data      								
    dataflow_next = dataflow_in[0,:,:]
    data_flow_tot = np.zeros([int(np.size(Runoff_in_m3_month,0)+1),size_Y, size_X])
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
    		
        print "still %s pixels to go" %int(np.nansum(dataflow_next))
				
        data_flow_tot += data_flow_round	

    print 'time', time.time() - time1

    # Seperate the array in a river array and the routed input    
    Accumulated_Pixels = data_flow_tot[0,:,:] * Basin
    Routed_Array = data_flow_tot[1:,:,:] * Basin	
			
    return(Accumulated_Pixels, Routed_Array)

def Graph_DEM_Distance_Discharge(Discharge_dict, Distance_dict, DEM_dict, River_dict, Startdate, Enddate, Reference_data):

    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection 

    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')
 
    River_dict_tot = dict()	
    DEM_dict_tot = dict()
    Discharge_dict_tot = dict()
    Distance_dict_tot = dict()
				
    for timestep in range(0, len(Dates)):
    
        River_dict_tot[timestep] = River_dict
        DEM_dict_tot[timestep] = DEM_dict
        Discharge_dict_one = dict()
        for river_part in Discharge_dict.iteritems():
            Discharge_dict_one[river_part[0]]= Discharge_dict[river_part[0]][timestep,:]
        Discharge_dict_tot[timestep] = Discharge_dict_one   
        Distance_dict_tot[timestep] = Distance_dict

    All_discharge_values = []
    for o in range(0,len(Dates)):
        for p in range(0,len(River_dict_tot[0])):
            Discharge_data_one = Discharge_dict_tot[o][p]
            All_discharge_values = np.append(All_discharge_values, Discharge_data_one)		

    for i in range(0, len(Dates)):
        Max_length_dict = len(River_dict_tot[i][max(River_dict_tot[i], key=lambda x:len(River_dict_tot[i][x]))])
        Data_3d = np.ones([len(River_dict_tot[i]), Max_length_dict, 2])*-9999
        Data_z_2d = np.ones([len(River_dict_tot[i]), Max_length_dict]) * np.nan
        for River_number in range(0,len(River_dict_tot[i])):													
            xData = Distance_dict_tot[i][River_number]/1000
            yData = DEM_dict_tot[i][River_number]
            zData =  Discharge_dict_tot[i][River_number]

            Data_3d[River_number,0:len(Distance_dict_tot[i][River_number]),0] = xData[:]
            Data_3d[River_number,0:len(Distance_dict_tot[i][River_number]),1] = yData[:]
            Data_z_2d[River_number,0:len(Distance_dict_tot[i][River_number])] = zData[:]
        # Mask some values to test masked array support:
        segs = np.ma.masked_where((Data_3d < -10), Data_3d)

        LineData = np.nanmin(Data_z_2d, axis = 1)

        LineWidth = ((LineData - np.min(All_discharge_values)) / (np.max(All_discharge_values) - np.min(All_discharge_values)) * (9) + 1)

        plt.figure(i)
        ax = plt.axes()

        minx = np.min(segs[:,:,0])
        maxx = np.max(segs[:,:,0])
        miny = np.min(segs[:,:,1])
        maxy = np.max(segs[:,:,1])
        ax.set_xlim(minx - (maxx - minx)/10, maxx + (maxx - minx)/10)
        ax.set_ylim(miny - (maxy - miny)/10, maxy + (maxy - miny)/10)

        line_segments = LineCollection(segs, LineWidth, linestyle='solid', cmap = plt.get_cmap('Spectral'), norm = plt.Normalize(np.min(All_discharge_values), np.max(All_discharge_values)))
        ax.add_collection(line_segments)
        ax.set_title('Timestep = %d' %i)
        line_segments.set_array(LineData)
        axcb = plt.colorbar(line_segments)
        plt.ylabel('Altitude in m')								
        plt.xlabel('Upstream distance in km')	
        plt.show()




















