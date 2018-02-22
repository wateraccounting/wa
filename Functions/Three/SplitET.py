# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2018
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Three
"""
def Blue_Green(Startdate, Enddate, Name_NC_LU, Name_NC_ETref, Name_NC_ET, Name_NC_P):
    '''
    # Input NC Rasters
    Name_NC_LU = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\LU_Simulation1_.nc'
    Name_NC_ETref = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\ETref_Simulation1_monthly_mm_082013_122014.nc'
    Name_NC_ET = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\ET_Simulation1_monthly_mm_012014_122014.nc'
    Name_NC_P = r'J:\\Create_Sheets\\Hong\\Simulations\\Simulation_1\\Sheet_3\\Prec_Simulation1_monthly_mm_082013_122014.nc'
    
    # Define start date and enddate for the WA+ sheets
    Startdate = "2014-01-01"
    Enddate = "2014-12-31"
    '''
    
    # import modules
    import wa.Functions.Start.Get_Dictionaries as GD
    import wa.General.raster_conversions as RC
    import numpy as np
    import pandas as pd

    # Input Parameters functions
    scale = 1.1

    # Define monthly dates
    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')
    
    # Get dictionaries and keys for the moving average
    ET_Blue_Green_Classes_dict, Moving_Window_Per_Class_dict = GD.get_bluegreen_classes(version = '1.0')
    Classes = ET_Blue_Green_Classes_dict.keys()
    
    # Open the NETCDF files that are needed
    LU = RC.Open_nc_array(Name_NC_LU)
    ET = RC.Open_nc_array(Name_NC_ET)    
    ETref = RC.Open_nc_array(Name_NC_ETref)
    P = RC.Open_nc_array(Name_NC_P)
    
    # Define empty arrays needed for the calculations
    ETref_Ave = np.ones([len(Dates),int(LU.shape[0]),int(LU.shape[1])]) * np.nan
    P_Ave = np.ones([len(Dates),int(LU.shape[0]),int(LU.shape[1])]) * np.nan
    Moving_Averages_Values_Array = np.ones(LU.shape) * np.nan
 
    # Create array based on the dictionary that gives the Moving average tail for every pixel
    for Class in Classes:
        Values_Moving_Window_Class = Moving_Window_Per_Class_dict[Class]
        for Values_Class in ET_Blue_Green_Classes_dict[Class]:
            Moving_Averages_Values_Array[LU == Values_Class] = Values_Moving_Window_Class

    # Loop over the different moving average tails    
    for One_Value in np.unique(Moving_Window_Per_Class_dict.values()):
        
        # If there is no moving average is 1 than use the value of the original ETref or P
        if One_Value == 1:
            Values_Ave_ETref = ETref[int(ETref.shape[0])-len(Dates):,:,:]
            Values_Ave_P = P[int(ETref.shape[0])-len(Dates):,:,:]

        # If there is tail, apply moving average over the whole datacube
        else:
            Values_Ave_ETref_tot = RC.Moving_average(ETref, One_Value - 1, 0)
            Values_Ave_P_tot = RC.Moving_average(P, One_Value - 1, 0)            
            Values_Ave_ETref = Values_Ave_ETref_tot[int(Values_Ave_ETref_tot.shape[0])-len(Dates):,:,:]
            Values_Ave_P = Values_Ave_P_tot[int(Values_Ave_P_tot.shape[0])-len(Dates):,:,:]
         
        # Only add the data where the corresponding tail corresponds with the one_value    
        ETref_Ave[:,Moving_Averages_Values_Array == One_Value] = Values_Ave_ETref[:,Moving_Averages_Values_Array == One_Value]
        P_Ave[:,Moving_Averages_Values_Array == One_Value] = Values_Ave_P[:,Moving_Averages_Values_Array == One_Value]

    # Mask out the nan values(if one of the parameters is nan, then they are all nan)
    mask = np.any([np.isnan(LU)*np.ones([len(Dates),int(LU.shape[0]),int(LU.shape[1])])==1, np.isnan(ET), np.isnan(ETref[int(ETref.shape[0])-len(Dates):,:,:]), np.isnan(P[int(ETref.shape[0])-len(Dates):,:,:]), np.isnan(P_Ave), np.isnan(ETref_Ave)],axis=0)           
    ETref[mask] = ETref_Ave[mask] = ET[mask] = P[mask] = P_Ave[mask] = np.nan            

    phi = ETref_Ave / P_Ave    

    # Calculate Budyko-index
    Budyko = scale * np.sqrt(phi*np.tanh(1/phi)*(1-np.exp(-phi)))

    # Calculate ET green
    ETgreen_DataCube = np.minimum(Budyko*P[int(ETref.shape[0])-len(Dates):,:,:],ET)

    # Calculate ET blue
    ETblue_DataCube = ET - ETgreen_DataCube
  
    return(ETblue_DataCube, ETgreen_DataCube)

