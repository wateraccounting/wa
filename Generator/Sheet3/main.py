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

def Calculate(Basin, P_Product, ET_Product, LAI_Product, NDM_Product, Moving_Averaging_Length, Startdate, Enddate, Simulation):
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
    import wa.Functions.Two as Two
    import wa.Functions.Start as Start
    import wa.Generator.Sheet3 as Generate
    
    ######################### Set General Parameters ##############################

    # Get environmental variable for the Home folder
    WA_env_paths = os.environ["WA_HOME"].split(';')
    Dir_Home = WA_env_paths[0]
	
    # Create the Basin folder
    Dir_Basin = os.path.join(Dir_Home, Basin)
    if not os.path.exists(Dir_Basin):
        os.makedirs(Dir_Basin)	

    # Get the boundaries of the basin based on the shapefile of the watershed
    # Boundaries, Shape_file_name_shp = Start.Boundaries.Determine(Basin)
    Boundaries, Example_dataset = Start.Boundaries.Determine_LU_Based(Basin)
    
    ############################# Download Data ###################################

    # Set the NPP and GPP data for the whole year
    StartYear = Startdate[:4]
    EndYear = Enddate[:4]
    StartdateNDM = '%d-01-01' %int(StartYear)
    EnddateNDM = '%d-12-31' %int(EndYear)

    #Set Startdate and Enddate for moving average
    Additional_Months = (Moving_Averaging_Length - 1)/2
    Startdate_Moving_Average = pd.Timestamp(Startdate) - pd.DateOffset(months = Additional_Months)
    Enddate_Moving_Average = pd.Timestamp(Enddate) + pd.DateOffset(months = Additional_Months)
    Startdate_Moving_Average_String = '%d-%02d-%02d' %(Startdate_Moving_Average.year, Startdate_Moving_Average.month, Startdate_Moving_Average.day)
    Enddate_Moving_Average_String = '%d-%02d-%02d' %(Enddate_Moving_Average.year, Enddate_Moving_Average.month, Enddate_Moving_Average.day)

    # Download data
    Data_Path_P = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, P_Product, Daily = 'n') 
    Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, ET_Product)
    Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_Moving_Average_String)
   
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

    ###################### Save Data as netCDF files ##############################
    
    #___________________________________Land Use_______________________________

    # Get the data of LU and save as nc, This dataset is also used as reference for others
    LUdest = gdal.Open(Example_dataset)    
    DataCube_LU = LUdest.GetRasterBand(1).ReadAsArray()

    Name_NC_LU = DC.Create_NC_name('LU', Simulation, Dir_Basin, 2)
    if not os.path.exists(Name_NC_LU):
        DC.Save_as_NC(Name_NC_LU, DataCube_LU, 'LU', Example_dataset)

    LUdest = None
    del DataCube_LU

    #______________________________Precipitation_______________________________

    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    # Precipitation data
    Name_NC_P = DC.Create_NC_name('Prec', Simulation, Dir_Basin, 2, info)
    if not os.path.exists(Name_NC_P):
	
        # Get the data of Precipitation and save as nc
        DataCube_Prec = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P_Monthly, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_P, DataCube_Prec, 'Prec', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Prec

    #_______________________________Evaporation________________________________

    # Evapotranspiration data
    Name_NC_ET = DC.Create_NC_name('ET', Simulation, Dir_Basin, 2, info)
    if not os.path.exists(Name_NC_ET):

        # Get the data of Evaporation and save as nc
        DataCube_ET = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ET, DataCube_ET, 'ET', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET

   #_______________________Reference Evaporation______________________________

    # Reference Evapotranspiration data
    Name_NC_ETref = DC.Create_NC_name('ETref', Simulation, Dir_Basin, 4, info)
    if not os.path.exists(Name_NC_ETref):

        # Get the data of Evaporation and save as nc
        DataCube_ETref = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate_Moving_Average_String, Enddate_Moving_Average_String, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ETref, DataCube_ETref, 'ETref', Example_dataset, Startdate_Moving_Average_String, Enddate_Moving_Average_String, 'monthly', 0.01)
        del DataCube_ETref

    #___________________________Normalized Dry Matter__________________________

    # Define info for the nc files
    info = ['monthly','kg_ha-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_NDM = DC.Create_NC_name('NDM', Simulation, Dir_Basin, 2, info)
    if not os.path.exists(Name_NC_NDM):

        # Get the data of Evaporation and save as nc
        DataCube_NDM = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_NDM, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_NDM, DataCube_NDM, 'NDM', Example_dataset, Startdate, Enddate, 'monthly', 100)
        del DataCube_NDM



















    ############################# Calculate Sheet 3 ###########################

    #____________ Evapotranspiration data split in ETblue and ETgreen ____________

    Name_NC_ETgreen = DC.Create_NC_name('ETgreen', Simulation, Dir_Basin, 4, info)
    Name_NC_ETblue = DC.Create_NC_name('ETblue', Simulation, Dir_Basin, 4, info)
    
    if not (os.path.exists(Name_NC_ETgreen) or os.path.exists(Name_NC_ETblue)):

        # Calculate Blue and Green ET
        DataCube_ETblue, DataCube_ETgreen = Four.SplitET.Blue_Green(Name_NC_ET, Name_NC_P, Name_NC_ETref, Startdate, Enddate, Additional_Months)

        # Save the ETblue and ETgreen data as NetCDF files
        DC.Save_as_NC(Name_NC_ETblue, DataCube_ETblue, 'ETblue', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        DC.Save_as_NC(Name_NC_ETgreen, DataCube_ETgreen, 'ETgreen', Example_dataset, Startdate, Enddate, 'monthly', 0.01)

        del DataCube_ETblue, DataCube_ETgreen
        
        
        
        
        
        
        
    
    ############################ Create CSV 3 #################################    

    Dir_Basin_CSV = Generate.CSV.Create(Dir_Basin, Simulation, Basin, Startdate, Enddate, Name_NC_LU, DataCube_I, DataCube_T, DataCube_E, Example_dataset)

    ############################ Create Sheet 3 ############################### 

    Generate.PDF.Create(Dir_Basin, Basin, Simulation, Dir_Basin_CSV)

    return()



















