# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Two
"""

def Calculate(WA_HOME_folder, Basin, P_Product, ET_Product, LAI_Product, NDM_Product, Startdate, Enddate, Simulation):
    """
    This functions is the main framework for calculating sheet 2.

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
    
    # import general python modules
    import os
    import gdal
    
    from wa.General import raster_conversions as RC
    from wa.General import data_conversions as DC
    import wa.Functions.Two as Two
    import wa.Functions.Start as Start
    import wa.Generator.Sheet2 as Generate
    
    ######################### Set General Parameters ##############################

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
    
    # Download data
    Data_Path_P = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, P_Product, Daily = 'y') 
    Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, ET_Product)
    Data_Path_LAI = Start.Download_Data.LAI(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate, Enddate, LAI_Product) 
    
    if NDM_Product == 'MOD17':
        Data_Path_NPP = Start.Download_Data.NPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], StartdateNDM, EnddateNDM, NDM_Product) 
        Data_Path_GPP = Start.Download_Data.GPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], StartdateNDM, EnddateNDM, NDM_Product) 

    Data_Path_P_Daily = os.path.join(Data_Path_P, 'Daily')
    Data_Path_P_Monthly = os.path.join(Data_Path_P, 'Monthly')
    
    ########################### Create input data #################################
    
    # Define info for the nc files
    info = ['monthly','days', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_RD = DC.Create_NC_name('RD', Simulation, Dir_Basin, 2, info)
    
    if not os.path.exists(Name_NC_RD):
        
        # Create Rainy Days based on daily CHIRPS
        Data_Path_RD = Two.Rainy_Days.Calc_Rainy_Days(Dir_Basin, Data_Path_P_Daily, Startdate, Enddate)

    # Create monthly LAI
    Dir_path_LAI = os.path.join(Dir_Basin, Data_Path_LAI)
    Start.Eightdaily_to_monthly_state.Nearest_Interpolate(Dir_path_LAI, Startdate, Enddate)

    # Define info for the nc files
    info = ['monthly','kg_ha-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_NC_NDM = DC.Create_NC_name('NDM', Simulation, Dir_Basin, 2, info)
    
    if not os.path.exists(Name_NC_NDM):

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

    #___________________________Normalized Dry Matter__________________________

    if not os.path.exists(Name_NC_NDM):

        # Get the data of Evaporation and save as nc
        DataCube_NDM = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_NDM, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_NDM, DataCube_NDM, 'NDM', Example_dataset, Startdate, Enddate, 'monthly', 100)
        del DataCube_NDM

    #_______________________________Rainy Days_________________________________

    if not os.path.exists(Name_NC_RD):

        # Get the data of Evaporation and save as nc
        DataCube_RD = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_RD, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_RD, DataCube_RD, 'RD', Example_dataset, Startdate, Enddate, 'monthly', 100)
        del DataCube_RD

    #_______________________________Leaf Area Index____________________________

    # Define info for the nc files
    info = ['monthly','m2-m-2', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_LAI = DC.Create_NC_name('LAI', Simulation, Dir_Basin, 2, info)
    if not os.path.exists(Name_NC_LAI):

        # Get the data of Evaporation and save as nc
        DataCube_LAI = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_LAI, Startdate, Enddate, Example_data = Example_dataset)
        DC.Save_as_NC(Name_NC_LAI, DataCube_LAI, 'LAI', Example_dataset, Startdate, Enddate, 'monthly', 1)
        del DataCube_LAI

    ############## Cut dates into pieces if it is needed ######################
    
    years = range(int(Startdate.split('-')[0]),int(Enddate.split('-')[0]) + 1)
    
    for year in years:
        
        if len(years) > 1.0:
        
            if year is years[0]:
                Startdate_part = Startdate
                Enddate_part = '%s-12-31' %year
            if year is years[-1]:
                Startdate_part = '%s-01-01' %year
                Enddate_part = Enddate               
                       
        else:
            Startdate_part = Startdate
            Enddate_part = Enddate

        ####################### Calculations Sheet 2 ##########################
    
        DataCube_I, DataCube_T, DataCube_E = Two.SplitET.ITE(Dir_Basin, Name_NC_ET, Name_NC_LAI, Name_NC_P, Name_NC_RD, Name_NC_NDM, Name_NC_LU, Startdate_part, Enddate_part, Simulation)
    
        ######################### Create CSV 2 ################################  

        Dir_Basin_CSV = Generate.CSV.Create(Dir_Basin, Simulation, Basin, Startdate, Enddate, Name_NC_LU, DataCube_I, DataCube_T, DataCube_E, Example_dataset)

    ############################ Create Sheet 2 ############################### 

    Generate.PDF.Create(Dir_Basin, Basin, Simulation, Dir_Basin_CSV)

    return()



















