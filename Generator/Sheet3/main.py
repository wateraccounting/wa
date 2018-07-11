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
import netCDF4

def Calculate(WA_HOME_folder, Basin, P_Product, ET_Product, LAI_Product, NDM_Product, NDVI_Product, ETref_Product, dict_crops, dict_non_crops, Startdate, Enddate, Simulation):
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
    import wa.Functions.Four as Four
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
    output_dir = os.path.join(Dir_Basin, "Simulations", "Simulation_%d" %Simulation)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the boundaries of the basin based on the shapefile of the watershed
    # Boundaries, Shape_file_name_shp = Start.Boundaries.Determine(Basin)
    Boundaries, Example_dataset = Start.Boundaries.Determine_LU_Based(Basin, Dir_Home)

    ############################# Download Data ###################################
    # Check the years that needs to be calculated
    years = range(int(Startdate.split('-')[0]),int(Enddate.split('-')[0]) + 1)

    # Find the maximum moving window value
    ET_Blue_Green_Classes_dict, Moving_Window_Per_Class_dict = GD.get_bluegreen_classes(version = '1.0')
    Additional_Months_tail = np.max(Moving_Window_Per_Class_dict.values())

    for year in years:

        # Create Start and End date for time chunk
        Startdate_part = '%d-01-01' %int(year)
        Enddate_part = '%s-12-31' %year

        # Create .nc file if not exists
        nc_outname = os.path.join(output_dir, "%d.nc" % year)
        if not os.path.exists(nc_outname):
            DC.Create_new_NC_file(nc_outname, Example_dataset, Basin)

        #Set Startdate for moving average
        if int(year) == int(years[0]):
            Startdate_Moving_Average = pd.Timestamp(Startdate) - pd.DateOffset(months = Additional_Months_tail)
            Startdate_Moving_Average_String = Startdate_Moving_Average.strftime('%Y-%m-%d')
        else:
            Startdate_Moving_Average_String = Startdate_part

        # Open variables in netcdf
        fh = netCDF4.Dataset(nc_outname)
        Variables_NC = [var for var in fh.variables]
        fh.close()

        # Download data
        if not "Precipitation" in Variables_NC:
            Data_Path_P_Monthly = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, P_Product)

        if not "Actual_Evapotransporation" in Variables_NC:
            Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, ET_Product)

        if not "Reference_Evapotranspiration" in Variables_NC:
            Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_part, ETref_Product)

        if not "NDVI" in Variables_NC:
            Data_Path_NDVI = Start.Download_Data.NDVI(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part)

        if not "Normalized_Dry_Matter" in Variables_NC:
            Data_Path_NPP = Start.Download_Data.NPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, NDM_Product)
            Data_Path_GPP = Start.Download_Data.GPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, NDM_Product)

        ########################### Create input data #################################

        if not "Normalized_Dry_Matter" in Variables_NC:
            # Create NDM based on MOD17
            if NDM_Product == 'MOD17':
                # Create monthly GPP
                Start.Eightdaily_to_monthly_state.Nearest_Interpolate(Data_Path_GPP, Startdate_part, Enddate_part)
                Data_Path_NDM = Two.Calc_NDM.NPP_GPP_Based(Dir_Basin, Data_Path_GPP, Data_Path_NPP, Startdate_part, Enddate_part)

        if not "NDVI" in Variables_NC:
            # Create monthly NDVI based on MOD13
            if NDVI_Product == 'MOD13':
                Start.Sixteendaily_to_monthly_state.Nearest_Interpolate(Data_Path_NDVI, Startdate_part, Enddate_part)

        ###################### Save Data as netCDF files ##############################
        #______________________________Precipitation_______________________________

        # 1.) Precipitation data
        if not "Precipitation" in Variables_NC:
            # Get the data of Precipitation and save as nc
            DataCube_Prec = RC.Get3Darray_time_series_monthly(Data_Path_P_Monthly, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Prec, "Precipitation", "mm/month", 0.01)
            del DataCube_Prec

        #_______________________________Evaporation________________________________

        # 2.) Evapotranspiration data
        if not "Actual_Evapotranspiration" in Variables_NC:
            # Get the data of Evaporation and save as nc
            DataCube_ET = RC.Get3Darray_time_series_monthly(Data_Path_ET, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ET, "Actual_Evapotranspiration", "mm/month", 0.01)
            del DataCube_ET

        #___________________________Normalized Dry Matter__________________________

        # 3.) Normalized Dry Matter
        if not "Normalized_Dry_Matter" in Variables_NC:
            # Get the data of Evaporation and save as nc
            DataCube_NDM = RC.Get3Darray_time_series_monthly(Data_Path_NDM, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_NDM, "Normalized_Dry_Matter", "kg_ha", 0.01)
            del DataCube_NDM

        #_______________________Reference Evaporation______________________________

        # 4.) Reference Evapotranspiration data
        if not "Reference_Evapotranspiration" in Variables_NC:
            # Get the data of Precipitation and save as nc
            DataCube_ETref = RC.Get3Darray_time_series_monthly(Data_Path_ETref, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ETref, "Reference_Evapotranspiration", "mm/month", 0.01)
            del DataCube_ETref

        #____________________________________NDVI__________________________________

         # 4.) Reference Evapotranspiration data
        if not "NDVI" in Variables_NC:
            # Get the data of Precipitation and save as nc
            DataCube_NDVI = RC.Get3Darray_time_series_monthly(Data_Path_NDVI, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_NDVI, "NDVI", "Fraction", 0.0001)
            del DataCube_NDVI

        ############################# Calculate Sheet 3 ###########################

        #____________ Evapotranspiration data split in ETblue and ETgreen ____________

        if not ("Blue_Evapotranspiration" in Variables_NC or "Green_Evapotranspiration" in Variables_NC):

            # Calculate Blue and Green ET
            DataCube_ETblue, DataCube_ETgreen = Four.SplitET.Blue_Green(Dir_Basin, nc_outname, ETref_Product, P_Product, Startdate, Enddate)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ETblue, "Blue_Evapotranspiration", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ETgreen, "Green_Evapotranspiration", "mm/month", 0.01)
            del DataCube_ETblue, DataCube_ETgreen

    #____________________________ Create the empty dictionaries ____________________________

    # Create the dictionaries that are required for sheet 3
    wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, wp_y_non_crop_dictionary = GD.get_sheet3_empties()

    #____________________________________ Fill in the dictionaries ________________________

    # Fill in the crops dictionaries
    wp_y_irrigated_dictionary, wp_y_rainfed_dictionary = Three.Fill_Dicts.Crop_Dictionaries(wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, dict_crops, nc_outname, Dir_Basin)

    # Fill in the non crops dictionaries
    wp_y_non_crop_dictionary = Three.Fill_Dicts.Non_Crop_Dictionaries(wp_y_non_crop_dictionary, dict_non_crops)

    ############################ Create CSV 3 #################################

    csv_fh_a, csv_fh_b = Generate.CSV.Create(wp_y_irrigated_dictionary, wp_y_rainfed_dictionary, wp_y_non_crop_dictionary, Basin, Simulation, year, Dir_Basin)


    ############################ Create Sheet 3 ###############################

    Generate.PDF.Create(Dir_Basin, Basin, Simulation, csv_fh_a, csv_fh_b)

    return()



















