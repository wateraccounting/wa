# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Three
"""
# import general python modules
import os
import gdal
import pandas as pd
import numpy as np

def Calculate(WA_HOME_folder, Basin, P_Product, ET_Product, LAI_Product, NDM_Product, NDVI_Product, dict_crops, dict_non_crops, Startdate, Enddate, Simulation):
    """
    This functions is the main framework for calculating sheet 3.

    Parameters
    ----------
    Basin : str
        Name of the basin
    P_Product : str
        Name of the rainfall product that will be used
    ET_Product : str
        Name of the evapotranspiration product that will be used
    LAI_Product : str
        Name of the LAI product that will be used        
    NDM_Product : str
        Name of the NDM product that will be used        
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Simulation : int
        Defines the simulation    
        
    """ 
    ######################### Import WA modules ###################################
    
    from wa.General import raster_conversions as RC
    from wa.General import data_conversions as DC
    import wa.Functions.Three as Three
    import wa.Functions.Two as Two
    import wa.Functions.Start as Start
    import wa.Generator.Sheet3 as Generate
    import wa.Functions.Start.Get_Dictionaries as GD
    
    ######################### Set General Parameters ##############################

    # Check if there is a full year selected  between Startdate and Enddate, otherwise Sheet 3 cannot be produced      
    try:
        years_end = pd.date_range(Startdate,Enddate,freq="A").year
        years_start = pd.date_range(Startdate,Enddate,freq="AS").year
        if (len(years_start) == 0 or len(years_end) == 0):
            print "Calculation period is less than a year, which is not possible for sheet 3"
            quit
        years = np.unique(np.append(years_end,years_start))
    except:
        print "Calculation period is less than a year, which is not possible for sheet 3"
        quit

    # Get environmental variable for the Home folder
    if WA_HOME_folder == '':
        WA_env_paths = os.environ["WA_HOME"].split(';')
        Dir_Home = WA_env_paths[0]
    else:
        Dir_Home = WA_HOME_folder
    	
    # Create the Basin folder
    Dir_Basin = os.path.join(Dir_Home, Basin)
    if not os.path.exists(Dir_Basin):
        os.makedirs(Dir_Basin)	

    # Get the boundaries of the basin based on the shapefile of the watershed
    # Boundaries, Shape_file_name_shp = Start.Boundaries.Determine(Basin)
    Boundaries, Example_dataset = Start.Boundaries.Determine_LU_Based(Basin, Dir_Home)
    
    ############################# Download Data ###################################

    # Set the NPP and GPP data for the whole year
    StartYear = Startdate[:4]
    EndYear = Enddate[:4]
    StartdateNDM = '%d-01-01' %int(StartYear)
    EnddateNDM = '%d-12-31' %int(EndYear)

    #Set Startdate and Enddate for moving average
    ET_Blue_Green_Classes_dict, Moving_Window_Per_Class_dict = GD.get_bluegreen_classes(version = '1.0')    
    Additional_Months_tail = np.max(Moving_Window_Per_Class_dict.values())
    Startdate_Moving_Average = pd.Timestamp(Startdate) - pd.DateOffset(months = Additional_Months_tail)
    Enddate_Moving_Average = pd.Timestamp(Enddate) + pd.DateOffset(months = 0)
    Startdate_Moving_Average_String = '%d-%02d-%02d' %(Startdate_Moving_Average.year, Startdate_Moving_Average.month, Startdate_Moving_Average.day)
    Enddate_Moving_Average_String = '%d-%02d-%02d' %(Enddate_Moving_Average.year, Enddate_Moving_Average.month, Enddate_Moving_Average.day)

    # Download data
    Data_Path_P = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_Moving_Average_String, P_Product, Daily = 'n') 
    Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, ET_Product)
    Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_Moving_Average_String)
    Data_Path_NDVI = Start.Download_Data.NDVI(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate)
    
    if NDM_Product == 'MOD17':
        Data_Path_NPP = Start.Download_Data.NPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], StartdateNDM, EnddateNDM, NDM_Product) 
        Data_Path_GPP = Start.Download_Data.GPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], StartdateNDM, EnddateNDM, NDM_Product) 

    Data_Path_P_Monthly = os.path.join(Data_Path_P, 'Monthly')
    
    ########################### Create input data #################################

    # Create NDM based on MOD17
    if NDM_Product == 'MOD17':

        # Create monthly GPP
        Dir_path_GPP = os.path.join(Dir_Basin, Data_Path_GPP)
        Start.Eightdaily_to_monthly_state.Nearest_Interpolate(Dir_path_GPP, StartdateNDM, EnddateNDM)
        Data_Path_NDM = Two.Calc_NDM.NPP_GPP_Based(Dir_Basin, Data_Path_GPP, Data_Path_NPP, Startdate, Enddate)

    # Create monthly NDVI based on MOD13
    if NDVI_Product == 'MOD13':
        Dir_path_NDVI = os.path.join(Dir_Basin, Data_Path_NDVI)
        Start.Sixteendaily_to_monthly_state.Nearest_Interpolate(Dir_path_NDVI, Startdate, Enddate)

    ###################### Save Data as netCDF files ##############################
    
    #___________________________________Land Use_______________________________

    # Get the data of LU and save as nc, This dataset is also used as reference for others
    LUdest = gdal.Open(Example_dataset)  
    DataCube_LU = LUdest.GetRasterBand(1).ReadAsArray()
    DataCube_LU[DataCube_LU<0] = np.nan

    Name_NC_LU = DC.Create_NC_name('LU', Simulation, Dir_Basin, 3)
    if not os.path.exists(Name_NC_LU):
        DC.Save_as_NC(Name_NC_LU, DataCube_LU, 'LU', Example_dataset)

    LUdest = None
    del DataCube_LU
    #_______________________________Evaporation________________________________

    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    # Evapotranspiration data
    Name_NC_ET = DC.Create_NC_name('ET', Simulation, Dir_Basin, 3, info)
    if not os.path.exists(Name_NC_ET):

        # Get the data of Evaporation and save as nc
        DataCube_ET = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ET, DataCube_ET, 'ET', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET

    #____________________________________NDVI__________________________________

    info = ['monthly','-', ''.join([Startdate_Moving_Average_String[5:7], Startdate_Moving_Average_String[0:4]]) , ''.join([Enddate_Moving_Average_String[5:7], Enddate_Moving_Average_String[0:4]])]


    Name_NC_NDVI = DC.Create_NC_name('NDVI', Simulation, Dir_Basin, 3, info)
    if not os.path.exists(Name_NC_NDVI):

        # Get the data of Evaporation and save as nc
        DataCube_NDVI = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_NDVI, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_NDVI, DataCube_NDVI, 'NDVI', Example_dataset, Startdate, Enddate, 'monthly', 1)
        del DataCube_NDVI

    #______________________________Precipitation_______________________________

    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate_Moving_Average_String[5:7], Startdate_Moving_Average_String[0:4]]) , ''.join([Enddate_Moving_Average_String[5:7], Enddate_Moving_Average_String[0:4]])]

    # Precipitation data
    Name_NC_P = DC.Create_NC_name('Prec', Simulation, Dir_Basin, 3, info)
    if not os.path.exists(Name_NC_P):
	
        # Get the data of Precipitation and save as nc
        DataCube_Prec = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P_Monthly, Startdate_Moving_Average_String, Enddate_Moving_Average_String, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_P, DataCube_Prec, 'Prec', Example_dataset, Startdate_Moving_Average_String, Enddate_Moving_Average_String, 'monthly', 0.01)
        del DataCube_Prec

   #________________________Reference Evaporation______________________________

    # Reference Evapotranspiration data
    Name_NC_ETref = DC.Create_NC_name('ETref', Simulation, Dir_Basin, 3, info)
    if not os.path.exists(Name_NC_ETref):

        # Get the data of Evaporation and save as nc
        DataCube_ETref = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate_Moving_Average_String, Enddate_Moving_Average_String, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ETref, DataCube_ETref, 'ETref', Example_dataset, Startdate_Moving_Average_String, Enddate_Moving_Average_String, 'monthly', 0.01)
        del DataCube_ETref

    #___________________________Normalized Dry Matter__________________________

    # Define info for the nc files
    info = ['monthly','kg_ha-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_NDM = DC.Create_NC_name('NDM', Simulation, Dir_Basin, 3, info)
    if not os.path.exists(Name_NC_NDM):

        # Get the data of Evaporation and save as nc
        DataCube_NDM = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_NDM, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_NDM, DataCube_NDM, 'NDM', Example_dataset, Startdate, Enddate, 'monthly', 100)
        del DataCube_NDM

    ############################# Calculate Sheet 3 ###########################

    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate_Moving_Average_String[5:7], Startdate_Moving_Average_String[0:4]]) , ''.join([Enddate_Moving_Average_String[5:7], Enddate_Moving_Average_String[0:4]])]

    #____________ Evapotranspiration data split in ETblue and ETgreen ____________

    Name_NC_ETgreen = DC.Create_NC_name('ETgreen', Simulation, Dir_Basin, 3, info)
    Name_NC_ETblue = DC.Create_NC_name('ETblue', Simulation, Dir_Basin, 3, info)
    
    if not (os.path.exists(Name_NC_ETgreen) or os.path.exists(Name_NC_ETblue)):

        # Calculate Blue and Green ET
        DataCube_ETblue, DataCube_ETgreen = Three.SplitET.Blue_Green(Startdate, Enddate, Name_NC_LU, Name_NC_ETref, Name_NC_ET, Name_NC_P)

        # Save the ETblue and ETgreen data as NetCDF files
        DC.Save_as_NC(Name_NC_ETblue, DataCube_ETblue, 'ETblue', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        DC.Save_as_NC(Name_NC_ETgreen, DataCube_ETgreen, 'ETgreen', Example_dataset, Startdate, Enddate, 'monthly', 0.01)

        del DataCube_ETblue, DataCube_ETgreen
        
    #____________________________ Create the empty dictionaries ____________________________
    
    # Create the dictionaries that are required for sheet 3    
    wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, wp_y_non_crop_dictionary = GD.get_sheet3_empties()
    
    #____________________________________ Fill in the dictionaries ________________________

    # Fill in the crops dictionaries   
    wp_y_irrigated_dictionary, wp_y_rainfed_dictionary = Three.Fill_Dicts.Crop_Dictionaries(wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, dict_crops, Name_NC_LU, Name_NC_ETgreen, Name_NC_ETblue, Name_NC_NDM, Name_NC_P, Dir_Basin)

    # Fill in the non crops dictionaries   
    wp_y_non_crop_dictionary = Three.Fill_Dicts.Non_Crop_Dictionaries(wp_y_non_crop_dictionary, dict_non_crops)

    for year in years:

    ############################ Create CSV 3 ################################# 
    
        csv_fh_a, csv_fh_b = Generate.CSV.Create(wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, wp_y_non_crop_dictionary, Basin, Simulation, year, Dir_Basin)

    ############################ Create Sheet 3 ############################### 

        Generate.PDF.Create(Dir_Basin, Basin, Simulation, csv_fh_a, csv_fh_b)
 
    return()



















