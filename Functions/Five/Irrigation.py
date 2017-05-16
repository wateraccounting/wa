# -*- coding: utf-8 -*-
"""
Created on Mon May 15 14:27:44 2017

@author: tih
"""

def Add_irrigation(Discharge_dict, River_dict, Name_NC_Rivers, Name_NC_ET, Name_NC_ETref, Name_NC_Prec, Example_dataset):

    import copy
    import numpy as np
    
    import wa.Functions.Five as Five
    import wa.Functions.Start as Start
    import wa.General.raster_conversions as RC
    
    # Copy dicts as starting adding reservoir 
    Discharge_dict_new = copy.deepcopy(Discharge_dict)

    # Extract Rivers data from NetCDF file
    Rivers = RC.Open_nc_array(Name_NC_Rivers)
    DataCube_ET = RC.Open_nc_array(Name_NC_ET)
        
    DataCube_ETgreen = Five.Budyko.Calc_ETgreen(Name_NC_ETref, Name_NC_Prec)
    DataCube_ETblue = DataCube_ET - DataCube_ETgreen
    DataCube_ETblue[DataCube_ETblue<0] = 0
                            
    # Open data array info based on example data
    geo_out, epsg, size_X, size_Y = RC.Open_array_info(Example_dataset)
       
    # Get Areas
    dlat, dlon = Start.Area_converter.Calc_dlat_dlon(geo_out, size_X, size_Y)                      
    array_m2 = dlat * dlon           
           
    DataCube_ETblue_m3 = DataCube_ETblue/1000 * array_m2
    
    # Create ID Matrix
    y,x = np.indices((size_Y, size_X))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y,size_X),mode='clip').reshape(x.shape))+1
    del  x, y
    
    # Find IDs
    ID_Rivers = Rivers * ID_Matrix
    
    # find IDs drainage
    ID_Rivers_flow = RC.gap_filling(ID_Rivers,NoDataValue = 0.)

    for i in np.unique(ID_Rivers_flow):
        if np.nansum(DataCube_ETblue[:,ID_Rivers_flow == i]) > 0:
            total_surface_withdrawal = np.nansum(DataCube_ETblue_m3[:,ID_Rivers_flow == i],1)
            
            # Find exact reservoir area in river directory
            for River_part in River_dict.iteritems():
                if len(np.argwhere(River_part[1] == i)) > 0:
                    row_discharge = np.argwhere(River_part[1]==i)[0][0]
                    Discharge_dict_new[River_part[0]][:,0:row_discharge] = Discharge_dict_new[River_part[0]][:,0:row_discharge] - total_surface_withdrawal[:,None] 
                    Discharge_dict_new[River_part[0]][Discharge_dict_new[River_part[0]]<=0] = 0
                    End_river = River_dict[River_part[0]][0]
                    times = 0
                    while len(River_dict) > times:
                        for River_part_downstream in River_dict.iteritems():
                            if River_dict[River_part[0]][-1] == End_river:  
                                print River_part_downstream
                                Discharge_dict_new[River_part_downstream[0]][:,1:] = Discharge_dict_new[River_part_downstream[0]][:,1:] - total_surface_withdrawal[:,None] 
                                Discharge_dict_new[River_part_downstream[0]][Discharge_dict_new[River_part_downstream[0]]<=0] = 0
                                End_river = River_dict[River_part_downstream[0]][0]
                                times = 0
                            times += 1
 
    return(Discharge_dict_new)                               