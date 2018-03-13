# -*- coding: utf-8 -*-
"""
Created on Mon May 15 14:27:44 2017

@author: tih
"""

def Calc_Supply_Budyko(Discharge_dict, Name_NC_Rivers, Name_NC_ET, Name_NC_ETref, Name_NC_Prec, Name_NC_Basin, Name_NC_frac_sw, Startdate, Enddate, Example_dataset):
    
    import wa.Functions.Five as Five
    import wa.Functions.Start as Start
    import wa.General.raster_conversions as RC
    
    # Extract Rivers data from NetCDF file
    DataCube_ET = RC.Open_nc_array(Name_NC_ET, Startdate = Startdate, Enddate = Enddate)
        
    DataCube_ETgreen = Five.Budyko.Calc_ETgreen(Name_NC_ETref, Name_NC_Prec, Name_NC_ET, Startdate, Enddate)
    DataCube_ETblue = DataCube_ET - DataCube_ETgreen
    DataCube_ETblue[DataCube_ETblue < 0] = 0
                            
    # Open data array info based on example data
    geo_out, epsg, size_X, size_Y = RC.Open_array_info(Example_dataset)
       
    # Get Areas
    dlat, dlon = Start.Area_converter.Calc_dlat_dlon(geo_out, size_X, size_Y)                      
    array_m2 = dlat * dlon                
    DataCube_ETblue_m3 = DataCube_ETblue/1000 * array_m2
    
    # Open array with surface water fractions
    DataCube_frac_sw = RC.Open_nc_array(Name_NC_frac_sw)
    
    # Total amount of ETblue taken out of rivers
    DataCube_surface_withdrawal_m3 = DataCube_ETblue_m3 * DataCube_frac_sw[None,:,:]
    
    return(DataCube_surface_withdrawal_m3, DataCube_ETblue_m3)
    
def Add_irrigation(Discharge_dict, River_dict, Name_NC_Rivers, Name_NC_Supply, Name_NC_ETblue, Name_NC_Basin, Startdate, Enddate, Example_dataset):
    #Discharge_dict_CR2, River_dict_CR2, Name_NC_Rivers_CR,  Name_NC_Supply, Name_NC_ETblue, Name_NC_Basin_CR, Startdate, Enddate, Example_dataset
    import copy
    import numpy as np
    import sys
    import wa.General.raster_conversions as RC
    
    # Copy dicts as starting adding reservoir 
    Discharge_dict_new = copy.deepcopy(Discharge_dict)

    # Extract Rivers data from NetCDF file
    Rivers = RC.Open_nc_array(Name_NC_Rivers)
    DataCube_surface_withdrawal_m3 = RC.Open_nc_array(Name_NC_Supply, Startdate = Startdate, Enddate = Enddate)
    DataCube_ETblue_m3 = RC.Open_nc_array(Name_NC_ETblue, Startdate = Startdate, Enddate = Enddate)

    # Open data array info based on example data
    geo_out, epsg, size_X, size_Y = RC.Open_array_info(Example_dataset)
  
    # Create ID Matrix
    y,x = np.indices((size_Y, size_X))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y,size_X),mode='clip').reshape(x.shape))+1
    del  x, y
    
    # Find IDs
    ID_Rivers = Rivers * ID_Matrix
    
    # find IDs drainage for only the basin
    Basin = RC.Open_nc_array(Name_NC_Basin)
    ID_Rivers_flow = RC.gap_filling(ID_Rivers,NoDataValue = 0.) * Basin
    Water_Error = 0 
    
    for i in np.unique(ID_Rivers_flow)[1:]:
        if np.nansum(DataCube_ETblue_m3[:,ID_Rivers_flow == i]) > 0:
            sys.stdout.write("\r%s Procent of adding irrigation completed with %s x 10^9 m3 Water Error       " %(np.int((i-np.unique(ID_Rivers_flow)[1])/(np.unique(ID_Rivers_flow)[-1]-np.unique(ID_Rivers_flow)[1])*100),Water_Error/1e9))
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