# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:45:45 2018

@author: tih
"""
import numpy as np
import wa.General.raster_conversions as RC

def Run(input_nc, output_nc):

    # Extract flow direction data from NetCDF file
    flow_directions = RC.Open_nc_array(input_nc, Var = 'demdir')

    # Open River Array
    Rivers = RC.Open_nc_array(output_nc, Var = 'rivers')

    # Open Accumulated Pixel Array
    Accumulated_Pixels = RC.Open_nc_array(output_nc, Var = 'accpix')

    # Open Routed discharge Array
    Routed_Array = RC.Open_nc_array(output_nc, Var = 'discharge_natural')

    # Get the raster shape
    geo_out_example, epsg_example, size_X_example, size_Y_example, size_Z_example, Time_example = RC.Open_nc_info(input_nc)
    geo_out_example = np.array(geo_out_example)

    # Create a river array with a boundary of 1 pixel
    Rivers_bounds = np.zeros([size_Y_example+2, size_X_example+2])
    Rivers_bounds[1:-1,1:-1] = Rivers

    # Create a flow direction array with a boundary of 1 pixel
    flow_directions[flow_directions==0]=-32768
    flow_directions_bound = np.ones([size_Y_example+2, size_X_example+2]) * -32768
    flow_directions_bound[1:-1,1:-1] = flow_directions

    # Create ID Matrix
    y,x = np.indices((size_Y_example, size_X_example))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y_example,size_X_example),mode='clip').reshape(x.shape))
    ID_Matrix_bound = np.ones([size_Y_example+2, size_X_example+2]) * -32768
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
        data_flow_to = np.zeros([size_Y_example + 2, size_X_example + 2])
        data_flow_from = np.zeros([size_Y_example + 2, size_X_example + 2])

        # Get the ID of only the rivers
        data_flow_to_ID = np.zeros([size_Y_example + 2, size_X_example + 2])
        data_flow_in = np.ones([size_Y_example + 2, size_X_example + 2])	* Rivers_bounds

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

    # Open Basin area
    Basin = RC.Open_nc_array(input_nc, Var = 'basin')
    Basin = -1 * (Basin - 1)
    Basin_Buffer = RC.Create_Buffer(Basin, 8)
    Possible_End_Points = np.zeros(Basin.shape)
    Possible_End_Points[(Basin_Buffer + Rivers) == 2] = 1
    End_Points = [[0,0]]

    rows_col_possible_end_pixels = np.argwhere(Possible_End_Points == 1)
    #  Accumulated_Pixels_possible = ID_Matrix * Possible_End_Points

    for PosPix in rows_col_possible_end_pixels:
        Accumulated_Pixels_possible_Area = Accumulated_Pixels[PosPix[0]-1:PosPix[0]+2, PosPix[1]-1:PosPix[1]+2]
        Max_acc_possible_area = np.max(Accumulated_Pixels_possible_Area)
        middle_pixel = Accumulated_Pixels_possible_Area[1,1]
        if Max_acc_possible_area == middle_pixel:
            if flow_directions[PosPix[0],PosPix[1]] == -32768:
                acc_aux = np.copy(Accumulated_Pixels_possible_Area)
                acc_aux[1,1] = 0
                off_y = np.where(acc_aux == np.max(acc_aux))[1][0] - 1
                off_x = np.where(acc_aux == np.max(acc_aux))[0][0] - 1
                PosPix[0] = PosPix[0] + off_x
                PosPix[1] = PosPix[1] + off_y
            if End_Points == []:
                End_Points = PosPix
            else:
                End_Points = np.vstack([End_Points, PosPix])

    # Create an empty dictionary for the rivers
    River_dict = dict()

    # Create empty array for the loop
    ID_starts_next = []
    i = 0

    for End_Point in End_Points[1:]:

    # Define starting point
    # Max_Acc_Pix = np.nanmax(Accumulated_Pixels[ID_Matrix_bound[1:-1,1:-1]>0])
    # ncol, nrow = np.argwhere(Accumulated_Pixels==Max_Acc_Pix)[0]

    # Add Bounds
    # col = ncol + 1
    # row = nrow + 1

        col = End_Point[0] + 1
        row = End_Point[1] + 1

        ############################ Route the river ##################################

        # Get the ID of the starting point
        ID_starts = [ID_Matrix_bound[col,row]]


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
                IDs = np.array([ID_from, ID_start])
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

    # Extract DEM data from NetCDF file
    DEM = RC.Open_nc_array(input_nc, Var = 'dem')

    # Get the distance of a horizontal and vertical flow pixel (assuming it flows in a straight line)
    import wa.Functions.Start.Area_converter as AC
    vertical, horizontal = AC.Calc_dlat_dlon(geo_out_example,size_X_example, size_Y_example)

    # Calculate a diagonal flowing pixel (assuming it flos in a straight line)
    diagonal = np.power((np.square(vertical) + np.square(horizontal)),0.5)

    # Create empty distance array
    Distance = np.zeros([size_Y_example, size_X_example])

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
            #Discharge_river[0] = Routed_Discharge[timestep, row - 1, col - 1]

        # For the other pixels get the value of the River ID pixel
        for River_part in River[1:]:
            row, col = np.argwhere(ID_Matrix_bound == River_part)[0][:]
            Distances_river[i] = Distance[row - 1, col - 1]
            DEM_river[i] = np.max([DEM_river[i-1],DEM[row - 1, col - 1]])
            #Discharge_river[i] = Routed_Discharge[timestep, row - 1, col - 1]

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


    ########################## Discharge Dictionary ###############################

    # Create ID Matrix
    y,x = np.indices((size_Y_example, size_X_example))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y_example,size_X_example),mode='clip').reshape(x.shape))
    ID_Matrix_bound = np.ones([size_Y_example+2, size_X_example+2]) * -32768
    ID_Matrix_bound[1:-1,1:-1] = ID_Matrix + 1
    del  x, y

    # Create empty dicionaries for discharge, distance, and DEM
    Discharge_dict = dict()

    Amount_months = len(RC.Open_nc_array(input_nc, Var = 'time'))

    # Loop over the branches
    for River_number in range(0,len(River_dict)):

        # Get the pixels associated with the river section
        River = River_dict[River_number]
        i=0

        # Create empty arrays
        Discharge_river = np.zeros([Amount_months, len(River)])

        # For the other pixels get the value of the River ID pixel
        for River_part in River[:]:
            row, col = np.argwhere(ID_Matrix_bound == River_part)[0][:]
            Discharge_river[:,i] = Routed_Array[:, row - 1, col - 1]
            i += 1

        # Write array in dictionary
        Discharge_dict[River_number] = Discharge_river
        print(River_number)

    return(DEM_dict, River_dict, Distance_dict, Discharge_dict)



