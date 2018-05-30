# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 15:27:12 2018

@author: tih
"""
import copy
import numpy as np
import sys
import wa.General.raster_conversions as RC

def Run(input_nc, output_nc):

    # Open discharge dict
    Discharge_dict = RC.Open_nc_dict(output_nc, 'dischargedict_dynamic')

    # Open River dict
    River_dict = RC.Open_nc_dict(output_nc, 'riverdict_static')

    # Open River Array
    Rivers = RC.Open_nc_array(output_nc, Var = 'rivers')

    # Open Supply Array
    DataCube_surface_withdrawal_mm = RC.Open_nc_array(input_nc, Var = 'Extraction_M')
    Areas_in_m2 = RC.Open_nc_array(input_nc, Var = 'area')
    DataCube_surface_withdrawal_m3 = ((DataCube_surface_withdrawal_mm/1000) * Areas_in_m2)

    # Open Basin Array
    Basin = RC.Open_nc_array(input_nc, Var = 'basin')

    # Copy dicts as starting adding reservoir
    Discharge_dict_new = copy.deepcopy(Discharge_dict)

    # Open data array info based on example data
    geo_out_example, epsg_example, size_X_example, size_Y_example, size_Z_example, Time_example = RC.Open_nc_info(input_nc)

    # Create ID Matrix
    y,x = np.indices((size_Y_example, size_X_example))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y_example,size_X_example),mode='clip').reshape(x.shape))+1
    del  x, y

    # Find IDs
    ID_Rivers = Rivers * ID_Matrix

    # find IDs drainage for only the basin
    ID_Rivers_flow = RC.gap_filling(ID_Rivers,NoDataValue = 0.) * Basin
    Water_Error = 0
    Count = 0

    for i in np.unique(ID_Rivers_flow)[1:]:
        Count += 1
        if np.nansum(DataCube_surface_withdrawal_m3[:,ID_Rivers_flow == i]) > 0:
            sys.stdout.write("\r%s Procent of adding irrigation completed with %.2f x 10^9 m3 Water Error       " %(np.int(np.ceil((np.float(Count)/len(np.unique(ID_Rivers_flow))*100))),Water_Error/1e9))
            sys.stdout.flush()
            #print('%s Procent of adding irrigation completed' %np.int(i/np.unique(ID_Rivers_flow)[-1]*100))
            total_surface_withdrawal = np.nansum(DataCube_surface_withdrawal_m3[:,ID_Rivers_flow == i] ,1)

            # Find exact area in river directory
            for River_part in River_dict.iteritems():
                if len(np.argwhere(River_part[1] == i)) > 0:

                    # Find the river part in the dictionery
                    row_discharge = np.argwhere(River_part[1]==i)[0][0]

                    # Subtract the withdrawal from that specific riverpart
                    Real_Surface_Withdrawal = np.minimum(Discharge_dict_new[River_part[0]][:,row_discharge].flatten(), total_surface_withdrawal[:,None].flatten())

                    Water_Error += np.maximum(np.nansum(total_surface_withdrawal[:,None].flatten() - Real_Surface_Withdrawal),0)
                    Discharge_dict_new[River_part[0]][:,0:row_discharge] = Discharge_dict_new[River_part[0]][:,0:row_discharge] - Real_Surface_Withdrawal[:,None]

                    # Subtract the withdrawal from the part downstream of the riverpart within the same dictionary
                    Discharge_dict_new[River_part[0]][np.logical_and(Discharge_dict_new[River_part[0]]<=0,Discharge_dict[River_part[0]]>=0)] = 0
                    End_river = River_dict[River_part[0]][0]
                    times = 0

                    # Subtract the withdrawal from all the other downstream dictionaries
                    while len(River_dict) > times:
                        for River_part_downstream in River_dict.iteritems():
                            if River_part_downstream[1][-1] == End_river:

                                Discharge_dict_new[River_part_downstream[0]][:,:] = Discharge_dict_new[River_part_downstream[0]][:,:] - Real_Surface_Withdrawal[:,None]
                                #Discharge_dict_new[River_part_downstream[0]][:,1:] = Discharge_dict_new[River_part_downstream[0]][:,1:] - total_surface_withdrawal[:,None]

                                Discharge_dict_new[River_part_downstream[0]][np.logical_and(Discharge_dict_new[River_part_downstream[0]]<=0,Discharge_dict[River_part_downstream[0]]>=0)] = 0
                                End_river = River_dict[River_part_downstream[0]][0]
                                times = 0
                            times += 1

    return(Discharge_dict_new)