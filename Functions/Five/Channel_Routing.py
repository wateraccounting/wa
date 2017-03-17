# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 10:47:16 2017

@author: tih
"""


import time
import numpy as np
import pandas as pd


from wa.General import raster_conversions as RC
from wa.General import data_conversions as DC

def Channel_Routing(Name_NC_DEM_Dir, Name_NC_Runoff, Name_NC_Basin, Reference_data, Degrees = 0):
    		
    time1 = time.time()

    # Extract runoff data from NetCDF file
    Runoff = RC.Open_nc_array(Name_NC_Runoff, Var = 'Runoff')

    # Extract flow direction data from NetCDF file
    flow_directions = RC.Open_nc_array(Name_NC_DEM_Dir, Var = 'DEM_Dir')
    
    # Extract basin data from NetCDF file	
    Basin = RC.Open_nc_array(Name_NC_Basin, Var = 'Basin')	 				
			
    if Degrees != 0:
	   
        import wa.Functions.Start.Area_converter as AC				
        # Convert area from degrees to m2									
        Areas_in_m2 = AC.Degrees_to_m2(Reference_data)
        Runoff_in_m3_month = ((Runoff/1000) * Areas_in_m2)

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

def Create_dict_rivers(Name_NC_DEM, Name_NC_DEM_Dir, Name_NC_Acc_Pixels, Name_NC_Rivers, Name_NC_Routed_Discharge, timestep, Reference_data):

    ############################### Open needed dataset ###########################
    
    # Extract discharge data from NetCDF file
    Routed_Discharge = RC.Open_nc_array(Name_NC_Routed_Discharge, Var = 'Routed_Discharge')
    
    # Extract flow direction data from NetCDF file
    flow_directions = RC.Open_nc_array(Name_NC_DEM_Dir, Var = 'DEM_Dir')
     
    # Extract Rivers data from NetCDF file
    Rivers = RC.Open_nc_array(Name_NC_Rivers, Var = 'Rivers')

    # Extract DEM data from NetCDF file
    DEM = RC.Open_nc_array(Name_NC_DEM, Var = 'DEM') 

    # Extract Accumulated pixels data from NetCDF file
    Accumulated_Pixels = RC.Open_nc_array(Name_NC_Acc_Pixels, Var = 'Acc_Pixels') 
			
    ############################### Create river tree #############################
        
    # Get the raster shape	
    size_Y, size_X = np.shape(flow_directions)
    
    # Create a river array with a boundary of 1 pixel
    Rivers_bounds = np.zeros([size_Y+2, size_X+2])
    Rivers_bounds[1:-1,1:-1] = Rivers	
    
    # Create a flow direction array with a boundary of 1 pixel
    flow_directions[flow_directions==0]=-32768
    flow_directions_bound = np.ones([size_Y+2, size_X+2]) * -32768
    flow_directions_bound[1:-1,1:-1] = flow_directions
    
    # Create ID Matrix
    y,x = np.indices((size_Y, size_X))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y,size_X),mode='clip').reshape(x.shape))
    ID_Matrix_bound = np.ones([size_Y+2, size_X+2]) * -32768
    ID_Matrix_bound[1:-1,1:-1] = ID_Matrix + 1
    ID_Matrix_bound[flow_directions_bound==-32768]=-32768
    del  x, y
    
    # Empty total from and to arrays
    ID_to_total=np.array([])
    ID_from_total=np.array([])
    
    # The flow directions parameters of HydroSHED
    Directions = [1, 2, 4, 8, 16, 32, 64, 128]
    
    # Loop over the directions			
    for Direction in Directions:
    
        # empty from and to arrays for 1 direction				
        data_flow_to = np.zeros([size_Y + 2, size_X + 2])
        data_flow_from = np.zeros([size_Y + 2, size_X + 2])
    				
        # Get the ID of only the rivers
        data_flow_to_ID = np.zeros([size_Y + 2, size_X + 2])			
        data_flow_in = np.ones([size_Y + 2, size_X + 2])	* Rivers_bounds	
    				
        # Mask only one direction				
        data_flow_from[flow_directions_bound == Direction] = data_flow_in[flow_directions_bound == Direction] * ID_Matrix_bound[flow_directions_bound == Direction]
    
        # Add the data flow to ID  
        if Direction == 4:
            data_flow_to[1:,:] = data_flow_from[:-1,:]
        if Direction == 2:
            data_flow_to[1:,1:] = data_flow_from[:-1,:-1]
        if Direction == 1:
            data_flow_to[:,1:] = data_flow_from[:,:-1]
        if Direction == 128:
            data_flow_to[:-1,1:] = data_flow_from[1:,:-1]
        if Direction == 64:
            data_flow_to[:-1,:] = data_flow_from[1:,:]
        if Direction == 32:
            data_flow_to[:-1,:-1] = data_flow_from[1:,1:]
        if Direction == 16:
            data_flow_to[:,:-1] = data_flow_from[:,1:]
        if Direction == 8:
            data_flow_to[1:,:-1] = data_flow_from[:-1,1:]
    
        # mask out the no river pixels
        data_flow_to_ID[data_flow_to>0] = ID_Matrix_bound[data_flow_to>0]
    
        # Collect to and from arrays
        ID_from_total = np.append(ID_from_total,data_flow_from[data_flow_from!=0].ravel())		
        ID_to_total = np.append(ID_to_total,data_flow_to_ID[data_flow_to_ID!=0].ravel())				
    
    
    ######################## Define the starting point ############################
    
    # Define starting point
    Max_Acc_Pix = np.nanmax(Accumulated_Pixels)
    ncol, nrow = np.argwhere(Accumulated_Pixels==Max_Acc_Pix)[0]  				

    # Add Bounds				
    col = ncol + 1
    row = nrow + 1
    
    ############################ Route the river ##################################
    
    # Get the ID of the starting point
    ID_starts = [ID_Matrix_bound[col,row]]
    
    # Create an empty dictionary for the rivers
    River_dict = dict()
    
    # Create empty array for the loop
    ID_starts_next = []	
    i = 0  
    
    # Keep going on till all the branches are looped
    while len(ID_starts) > 0:
        for ID_start in ID_starts:
            ID_start = int(ID_start)
    								
            # Empty parameters for new starting point								
            new = 0
            IDs = []	
    								
            # Add starting point								
            Arrays_from = np.argwhere(ID_from_total[:] == ID_start)             
            ID_from = ID_to_total[int(Arrays_from[0])]							
            IDs = [ID_from, ID_start]
            ID_start_now = ID_start	
    
            # Keep going till the branch ends								
            while new == 0:					
     
                Arrays_to = np.argwhere(ID_to_total[:] == ID_start)
    
                # Add IDs to the river dictionary
                if len(Arrays_to)>1 or len(Arrays_to) == 0:
                    River_dict[i] = IDs
                    i += 1	
                    new = 1
     
                    # Define the next loop for the new branches             											
                    for j in range(0, len(Arrays_to)):													
                        ID_starts_next = np.append(ID_starts_next,ID_from_total[int(Arrays_to[j])])												
    
                    # If it was the last one then empty ID_start_next                               																								
                    if ID_start_now == ID_starts[-1]:
                        ID_starts = ID_starts_next
                        ID_starts_next = []	
    
                # Add pixel to tree for river dictionary						
                else:
                    ID_start = ID_from_total[Arrays_to[0]]						
                    IDs = np.append(IDs, ID_start)									
         
									
    ######################## Create dict distance and dict dem ####################							
    
    # Get the distance of a horizontal and vertical flow pixel (assuming it flows in a straight line)
    import wa.Functions.Start.Area_converter as AC
    vertical, horizontal = AC.Calc_dlat_dlon(Reference_data)
    
    # Calculate a diagonal flowing pixel (assuming it flos in a straight line)
    diagonal = np.power((np.square(vertical) + np.square(horizontal)),0.5)
    
    # Create empty distance array
    Distance = np.zeros([size_Y, size_X])
    
    # Fill in the distance array
    Distance[np.logical_or(flow_directions == 1,flow_directions == 16)] = horizontal[np.logical_or(flow_directions == 1,flow_directions == 16)]
    Distance[np.logical_or(flow_directions == 64,flow_directions == 4)] = vertical[np.logical_or(flow_directions == 64,flow_directions == 4)]
    Distance[np.logical_or(np.logical_or(np.logical_or(flow_directions == 32,flow_directions == 8),flow_directions == 128),flow_directions == 2)] = diagonal[np.logical_or(np.logical_or(np.logical_or(flow_directions == 32,flow_directions == 8),flow_directions == 128),flow_directions == 2)]						
    
    # Create empty dicionaries for discharge, distance, and DEM
    Discharge_dict = dict()
    Distance_dict = dict()
    DEM_dict = dict()
        
    # Create empty arrays needed for the loop
    River_end = []
    River_ends = np.zeros([2,3])
    
    # Loop over the branches
    for River_number in range(0,len(River_dict)):
	    
        # Get the pixels associated with the river section    
        River = River_dict[River_number]
        i=1	
	    			
        # Create empty arrays				
        Distances_river = np.zeros([len(River)])
        DEM_river = np.zeros([len(River)])	
        Discharge_river = np.zeros([len(River)])	
        
        # for the first pixel get the previous pixel value from another branche				
        row_start = np.argwhere(River_ends[:,0] == River[0])	
        if len(row_start) < 1:			
            Distances_river[0] = 0
            row, col = np.argwhere(ID_Matrix_bound == River[0])[0][:]
            DEM_river[0] = DEM[row - 1, col - 1] 
            Discharge_river[0] = -9999        
					
        else:
            Distances_river[0] = River_ends[row_start, 1]
            DEM_river[0] = River_ends[row_start, 2]
            row, col = np.argwhere(ID_Matrix_bound == River[0])[0][:]
            Discharge_river[0] = Routed_Discharge[timestep, row - 1, col - 1] 	

        # For the other pixels get the value of the River ID pixel								
        for River_part in River[1:]:
            row, col = np.argwhere(ID_Matrix_bound == River_part)[0][:]
            Distances_river[i] = Distance[row - 1, col - 1]						
            DEM_river[i] = np.max([DEM_river[i-1],DEM[row - 1, col - 1]])  
            Discharge_river[i] = Routed_Discharge[timestep, row - 1, col - 1]								
    
            if River_part == River[1] and Discharge_river[i-1] == -9999:
                Discharge_river[i - 1] = Discharge_river[i]         
  													
            i += 1

        # Write array in dictionary													
        DEM_dict[River_number] = DEM_river
        Discharge_dict[River_number] = Discharge_river 
        Distance_dict[River_number] = np.cumsum(Distances_river)
				
        # Save the last pixel value				
        River_end[:] = [River_part , np.cumsum(Distances_river)[-1], DEM_river[-1]]								
        River_ends = np.vstack((River_ends, River_end))	

    return(River_dict, DEM_dict, Discharge_dict, Distance_dict)


def Graph_DEM_Distance_Discharge(Name_NC_DEM, Name_NC_DEM_Dir, Name_NC_Acc_Pixels, Name_NC_Rivers, Name_NC_Routed_Discharge, Startdate, Enddate, Reference_data):

    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection 

    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')
 
    River_dict_tot = dict()	
    DEM_dict_tot = dict()
    Discharge_dict_tot = dict()
    Distance_dict_tot = dict()
				
    for timestep in range(0, len(Dates)):
    
        River_dict, DEM_dict, Discharge_dict, Distance_dict = Create_dict_rivers(Name_NC_DEM, Name_NC_DEM_Dir, Name_NC_Acc_Pixels, Name_NC_Rivers, Name_NC_Routed_Discharge, timestep, Reference_data)

        River_dict_tot[timestep] = River_dict
        DEM_dict_tot[timestep] = DEM_dict 
        Discharge_dict_tot[timestep] = Discharge_dict
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




















