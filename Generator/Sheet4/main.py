# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Four
"""
# import general python modules
import os
import gdal
import pandas as pd

def Calculate(Basin, P_Product, ET_Product, Moving_Averaging_Length, Startdate, Enddate, Simulation):
    """
    This functions is the main framework for calculating sheet 4.

    Parameters
    ----------
    Basin : str
        Name of the basin
    P_Product : str
        Name of the rainfall product that will be used
    ET_Product : str
        Name of the evapotranspiration product that will be used 
    Moving_Averiging_Length, int
        Defines the length of the moving average    
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
    import wa.Functions.Four as Four
    import wa.Functions.Start as Start
    import wa.Generator.Sheet4 as Generate
    
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
 
    #Set Startdate and Enddate for moving average
    Additional_Months = (Moving_Averaging_Length - 1)/2
    Startdate_Moving_Average = pd.Timestamp(Startdate) - pd.DateOffset(months = Additional_Months)
    Enddate_Moving_Average = pd.Timestamp(Enddate) + pd.DateOffset(months = Additional_Months)
    Startdate_Moving_Average_String = '%d-%02d-%02d' %(Startdate_Moving_Average.year, Startdate_Moving_Average.month, Startdate_Moving_Average.day)
    Enddate_Moving_Average_String = '%d-%02d-%02d' %(Enddate_Moving_Average.year, Enddate_Moving_Average.month, Enddate_Moving_Average.day)

    ############################# Download Data ###################################

    # Download data
    Data_Path_P = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_Moving_Average_String, P_Product, Daily = 'n') 
    Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, ET_Product)
    Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_Moving_Average_String)
    Data_Path_GWF = Start.Download_Data.GWF(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']])

    Data_Path_P_Monthly = os.path.join(Data_Path_P, 'Monthly')

    ###################### Save Data as netCDF files ##############################
    
    #___________________________________Land Use_______________________________

    # Get the data of LU and save as nc, This dataset is also used as reference for others
    LUdest = gdal.Open(Example_dataset)    
    DataCube_LU = LUdest.GetRasterBand(1).ReadAsArray()

    Name_NC_LU = DC.Create_NC_name('LU', Simulation, Dir_Basin, 4)
    if not os.path.exists(Name_NC_LU):
        DC.Save_as_NC(Name_NC_LU, DataCube_LU, 'LU', Example_dataset)

    LUdest = None
    del DataCube_LU

    #______________________________Precipitation_______________________________

    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate_Moving_Average_String[5:7], Startdate_Moving_Average_String[0:4]]) , ''.join([Enddate_Moving_Average_String[5:7], Enddate_Moving_Average_String[0:4]])]

    # Precipitation data
    Name_NC_P = DC.Create_NC_name('Prec', Simulation, Dir_Basin, 4, info)
    if not os.path.exists(Name_NC_P):
	
        # Get the data of Precipitation and save as nc
        DataCube_Prec = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P_Monthly, Startdate_Moving_Average_String, Enddate_Moving_Average_String, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_P, DataCube_Prec, 'Prec', Example_dataset, Startdate_Moving_Average_String, Enddate_Moving_Average_String, 'monthly', 0.01)
        del DataCube_Prec

  #_______________________Reference Evaporation______________________________

    # Reference Evapotranspiration data
    Name_NC_ETref = DC.Create_NC_name('ETref', Simulation, Dir_Basin, 4, info)
    if not os.path.exists(Name_NC_ETref):

        # Get the data of Evaporation and save as nc
        DataCube_ETref = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate_Moving_Average_String, Enddate_Moving_Average_String, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ETref, DataCube_ETref, 'ETref', Example_dataset, Startdate_Moving_Average_String, Enddate_Moving_Average_String, 'monthly', 0.01)
        del DataCube_ETref

    #_______________________________Evaporation________________________________
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    # Evapotranspiration data
    Name_NC_ET = DC.Create_NC_name('ET', Simulation, Dir_Basin, 4, info)
    if not os.path.exists(Name_NC_ET):

        # Get the data of Evaporation and save as nc
        DataCube_ET = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_ET, DataCube_ET, 'ET', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET

    #_____________________________________GWF__________________________________

    # GWF data
    Name_NC_GWF = DC.Create_NC_name('GWF_Fraction', Simulation, Dir_Basin, 4)
    if not os.path.exists(Name_NC_GWF):

        # Get the data of GWF, reproject and save as nc
        GWF_Filepath = os.path.join(Dir_Basin, Data_Path_GWF, "Gray_Water_Footprint_Fraction.tif")
        dest_GWF = RC.reproject_dataset_example(GWF_Filepath, Example_dataset, method=1)
        DataCube_GWF = dest_GWF.GetRasterBand(1).ReadAsArray()
        DC.Save_as_NC(Name_NC_GWF, DataCube_GWF, 'GWF', Example_dataset,Scaling_factor = 0.01)

    ####################### Calculations Sheet 4 ##############################

    # Evapotranspiration data
    Name_NC_ETgreen = DC.Create_NC_name('ETgreen', Simulation, Dir_Basin, 4, info)
    Name_NC_ETblue = DC.Create_NC_name('ETblue', Simulation, Dir_Basin, 4, info)
    
    if not os.path.exists(Name_NC_ETgreen) or os.path.exists(Name_NC_ETblue):

        # Calculate Blue and Green ET
        DataCube_ETblue, DataCube_ETgreen = Four.SplitET.Blue_Green(Name_NC_ET, Name_NC_P, Name_NC_ETref, Startdate, Enddate, Additional_Months)

        # Get the data of Evaporation and save as nc
        DC.Save_as_NC(Name_NC_ETblue, DataCube_ETblue, 'ETblue', Example_dataset, Startdate, Enddate, 'monthly', 0.01)
        DC.Save_as_NC(Name_NC_ETgreen, DataCube_ETgreen, 'ETgreen', Example_dataset, Startdate, Enddate, 'monthly', 0.01)

    else:
        DataCube_ETblue = RC.Open_nc_array(Name_NC_ETblue, Var=None, Startdate = Startdate, Enddate = Enddate)
        DataCube_ETgreen = RC.Open_nc_array(Name_NC_ETgreen, Var=None, Startdate = Startdate, Enddate = Enddate)

    # Calculate non-consumend and Total supply maps by using fractions and consumed maps (blue ET)

    # Apply fractions over total supply to calculate gw and sw supply
    
    # Apply gray water footprint fractions to calculated non recoverable flow based on the non consumed flow
    
    # Apply fractions to calculate the recovarable SW/GW and non recovarable SW/GW
    
       
    ############################ Create CSV 4 #################################    

    Dir_Basin_CSV = Generate.CSV.Create(Dir_Basin, Simulation, Basin, Startdate, Enddate, Name_NC_LU, DataCube_ETblue, DataCube_ETgreen, Example_dataset)

    ############################ Create Sheet 4 ############################### 

    Generate.PDF.Create(Dir_Basin, Basin, Simulation, Dir_Basin_CSV)

    return()






















