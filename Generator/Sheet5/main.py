# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:07:52 2017

@author: tih
"""

def Calculate(WA_HOME_folder, Basin, P_Product, ET_Product, ETref_Product, DEM_Product, Water_Occurence_Product, Inflow_Text_Files, WaterPIX_filename, Reservoirs_GEE_on_off, Supply_method, Startdate, Enddate, Simulation):
    '''
    This functions consists of the following sections:
    1. Set General Parameters
    2. Download Data
    3. Convert the RAW data to NETCDF files
    4. Run SurfWAT

    '''
    # import General modules
    import os
    import gdal
    import numpy as np
    import pandas as pd
    from netCDF4 import Dataset

    # import WA plus modules
    from wa.General import raster_conversions as RC
    from wa.General import data_conversions as DC
    import wa.Functions.Five as Five
    import wa.Functions.Start as Start
    import wa.Functions.Start.Get_Dictionaries as GD

    ######################### 1. Set General Parameters ##############################

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
    geo_out, proj, size_X, size_Y = RC.Open_array_info(Example_dataset)

    # Define resolution of SRTM
    Resolution = '15s'

    # Find the maximum moving window value
    ET_Blue_Green_Classes_dict, Moving_Window_Per_Class_dict = GD.get_bluegreen_classes(version = '1.0')
    Additional_Months_tail = np.max(Moving_Window_Per_Class_dict.values())

    ############## Cut dates into pieces if it is needed ######################

    # Check the years that needs to be calculated
    years = range(int(Startdate.split('-')[0]),int(Enddate.split('-')[0]) + 1)

    for year in years:

        # Create .nc file if not exists
        nc_outname = os.path.join(output_dir, "%d.nc" % year)
        if not os.path.exists(nc_outname):
            DC.Create_new_NC_file(nc_outname, Example_dataset, Basin)

        # Open variables in netcdf
        fh = Dataset(nc_outname)
        Variables_NC = [var for var in fh.variables]
        fh.close()

        # Create Start and End date for time chunk
        Startdate_part = '%d-01-01' %int(year)
        Enddate_part = '%s-12-31' %int(year)

        if int(year) == int(years[0]):
            Startdate_Moving_Average = pd.Timestamp(Startdate) - pd.DateOffset(months = Additional_Months_tail)
            Startdate_Moving_Average_String = Startdate_Moving_Average.strftime('%Y-%m-%d')
        else:
            Startdate_Moving_Average_String = Startdate_part

        ############################# 2. Download Data ###################################

        # Download data
        if not "Precipitation" in Variables_NC:
            Data_Path_P_Monthly = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, P_Product)

        if not "Actual_Evapotranspiration" in Variables_NC:
            Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, ET_Product)

        if (WaterPIX_filename == "" or Supply_method == "Fraction") and not ("Reference_Evapotranspiration" in Variables_NC):
            Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_part, ETref_Product)

        if Reservoirs_GEE_on_off == 1 and not ("Water_Occurrence" in Variables_NC):
            Data_Path_JRC_occurrence = Start.Download_Data.JRC_occurrence(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Water_Occurence_Product)
            input_JRC = os.path.join(Data_Path_JRC_occurrence, "JRC_Occurrence_percent.tif")
        else:
            input_JRC = None

        # WaterPIX input
        Data_Path_DEM_Dir = Start.Download_Data.DEM_Dir(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution, DEM_Product)
        Data_Path_DEM = Start.Download_Data.DEM(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Resolution, DEM_Product)

        ###################### 3. Convert the RAW data to NETCDF files ##############################
        # The sequence of converting the data into netcdf is:
        # Precipitation
        # Evapotranspiration
        # Reference Evapotranspiration
        # DEM flow directions

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

        #_______________________Reference Evaporation______________________________

        # 3.) Reference Evapotranspiration data
        if (WaterPIX_filename == "" or Supply_method == "Fraction") and not ("Reference_Evapotranspiration" in Variables_NC):
            # Get the data of Precipitation and save as nc
            DataCube_ETref = RC.Get3Darray_time_series_monthly(Data_Path_ETref, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ETref, "Reference_Evapotranspiration", "mm/month", 0.01)
            del DataCube_ETref

        #____________________________fraction surface water _______________________

        DataCube_frac_sw = np.ones([size_Y, size_X]) * np.nan

        import wa.Functions.Start.Get_Dictionaries as GD

        # Open LU dataset
        DataCube_LU = RC.Open_nc_array(nc_outname, "Landuse")

        # Get dictionaries and keys
        lulc = GD.get_sheet5_classes()
        lulc_dict = GD.get_sheet5_classes().keys()
        consumed_frac_dict = GD.sw_supply_fractions()

        for key in lulc_dict:
            Numbers = lulc[key]
            for LU_nmbr in Numbers:
                DataCube_frac_sw[DataCube_LU==LU_nmbr] = consumed_frac_dict[key]

        DC.Add_NC_Array_Static(nc_outname, DataCube_frac_sw, "Fraction_Surface_Water_Supply", "fraction", 0.01)
        del DataCube_frac_sw, DataCube_LU

        ################### 4. Calculate Runoff (2 methods: a = Budyko and b = WaterPIX) #####################

        ################ 4a. Calculate Runoff based on Precipitation and Evapotranspiration ##################

        if (Supply_method == "Fraction" and not "Surface_Runoff" in Variables_NC):

            # Calculate runoff based on Budyko
            DataCube_Runoff = Five.Fraction_Based.Calc_surface_runoff(Dir_Basin, nc_outname, Startdate_part, Enddate_part, Example_dataset, ETref_Product, P_Product)

            # Save the runoff as netcdf
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Runoff, "Surface_Runoff", "mm/month", 0.01)
            del DataCube_Runoff

        ###################### 4b. Get Runoff from WaterPIX ###########################
        if (Supply_method == "WaterPIX" and not "Surface_Runoff" in Variables_NC):

            # Get WaterPIX data
            WaterPIX_Var = 'TotalRunoff_M'
            DataCube_Runoff = Five.Read_WaterPIX.Get_Array(WaterPIX_filename, WaterPIX_Var, Example_dataset, Startdate_part, Enddate_part)

            # Save the runoff as netcdf
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Runoff, "Surface_Runoff", "mm/month", 0.01)
            del DataCube_Runoff

        ####################### 5. Calculate Extraction (2 methods: a = Fraction, b = WaterPIX) #############################

        ###################### 5a. Get extraction from fraction method by using budyko ###########################
        if (Supply_method == "Fraction" and not "Surface_Withdrawal" in Variables_NC):
            DataCube_surface_withdrawal = Five.Fraction_Based.Calc_surface_withdrawal(Dir_Basin, nc_outname, Startdate_part, Enddate_part, Example_dataset, ETref_Product, P_Product)

            # Save the runoff as netcdf
            DC.Add_NC_Array_Variable(nc_outname, DataCube_surface_withdrawal, "Surface_Withdrawal", "mm/month", 0.01)
            del DataCube_surface_withdrawal

        #################################### 5b. Get extraction from WaterPIX ####################################
        if (Supply_method == "WaterPIX" and not "Surface_Withdrawal" in Variables_NC):
            WaterPIX_Var = 'Supply_M'
            DataCube_Supply = Five.Read_WaterPIX.Get_Array(WaterPIX_filename, WaterPIX_Var, Example_dataset, Startdate, Enddate)

            # Open array with surface water fractions
            DataCube_frac_sw = RC.Open_nc_array(nc_outname, "Fraction_Surface_Water_Supply")

            # Total amount of ETblue taken out of rivers
            DataCube_surface_withdrawal = DataCube_Supply * DataCube_frac_sw[None,:,:]

            # Save the runoff as netcdf
            DC.Add_NC_Array_Variable(nc_outname, DataCube_surface_withdrawal, "Surface_Withdrawal", "mm/month", 0.01)
            del DataCube_surface_withdrawal

        ################################## 5. Run SurfWAT #####################################

        import wa.Models.SurfWAT as SurfWAT

        # Define formats of input data
        Format_DEM = "TIFF"    # or "TIFF"
        Format_Runoff = "NetCDF"    # or "TIFF"
        Format_Extraction = "NetCDF"    # or "TIFF"
        Format_DEM_dir = "TIFF"    # or "TIFF"
        Format_Basin = "NetCDF"    # or "TIFF"

        # Give path (for tiff) or file (netcdf)
        input_nc = os.path.join(Dir_Basin, "Simulations", "Simulation_%s"%Simulation,"SurfWAT_in_%d.nc" %year)
        output_nc = os.path.join(Dir_Basin, "Simulations", "Simulation_%s"%Simulation,"SurfWAT_out_%d.nc" %year)

        # Create Input File for SurfWAT
        SurfWAT.Create_input_nc.main(Data_Path_DEM_Dir,
                                     Data_Path_DEM,
                                     os.path.dirname(nc_outname),
                                     os.path.dirname(nc_outname),
                                     os.path.dirname(nc_outname),
                                     Startdate,
                                     Enddate,
                                     input_nc,
                                     Resolution,
                                     Format_DEM_dir,
                                     Format_DEM,
                                     Format_Basin,
                                     Format_Runoff,
                                     Format_Extraction)

        # Run SurfWAT
        SurfWAT.Run_SurfWAT.main(input_nc, output_nc, input_JRC, Inflow_Text_Files, Reservoirs_GEE_on_off)



























    '''
    ################################# Plot graph ##################################

    # Draw graph
    Five.Channel_Routing.Graph_DEM_Distance_Discharge(Discharge_dict_CR3, Distance_dict_CR2, DEM_dict_CR2, River_dict_CR2, Startdate, Enddate, Example_dataset)

    ######################## Change data to fit the LU data #######################

    # Discharge
    # Define info for the nc files
    info = ['monthly','m3-month-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Discharge = DC.Create_NC_name('DischargeEnd', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Discharge):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_Discharge_CR = DC.Convert_dict_to_array(River_dict_CR2, Discharge_dict_CR3, Example_dataset)
        DC.Save_as_NC(Name_NC_Discharge, DataCube_Discharge_CR, 'Discharge_End_CR', Example_dataset, Startdate, Enddate, 'monthly')
        del DataCube_Discharge_CR


    '''





























    '''

    # DEM
    Name_NC_DEM = DC.Create_NC_name('DEM', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_DEM):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_DEM_CR = RC.Open_nc_array(Name_NC_DEM_CR)
        DataCube_DEM = RC.resize_array_example(DataCube_DEM_CR, LU_data, method=1)
        DC.Save_as_NC(Name_NC_DEM, DataCube_DEM, 'DEM', LU_dataset)
        del DataCube_DEM

    # flow direction
    Name_NC_DEM_Dir = DC.Create_NC_name('DEM_Dir', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_DEM_Dir):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_DEM_Dir_CR = RC.Open_nc_array(Name_NC_DEM_Dir_CR)
        DataCube_DEM_Dir = RC.resize_array_example(DataCube_DEM_Dir_CR, LU_data, method=1)
        DC.Save_as_NC(Name_NC_DEM_Dir, DataCube_DEM_Dir, 'DEM_Dir', LU_dataset)
        del DataCube_DEM_Dir

    # Precipitation
    # Define info for the nc files
    info = ['monthly','mm', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Prec = DC.Create_NC_name('Prec', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_Prec):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_Prec = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_P_Monthly, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_Prec, DataCube_Prec, 'Prec', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_Prec

    # Evapotranspiration
    Name_NC_ET = DC.Create_NC_name('ET', Simulation, Dir_Basin, 5)
    if not os.path.exists(Name_NC_ET):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ET = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ET, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_ET, DataCube_ET, 'ET', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ET

    # Reference Evapotranspiration data
    Name_NC_ETref = DC.Create_NC_name('ETref', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_ETref):

        # Get the data of Reference Evapotranspiration and save as nc
        DataCube_ETref = RC.Get3Darray_time_series_monthly(Dir_Basin, Data_Path_ETref, Startdate, Enddate, LU_dataset)
        DC.Save_as_NC(Name_NC_ETref, DataCube_ETref, 'ETref', LU_dataset, Startdate, Enddate, 'monthly', 0.01)
        del DataCube_ETref

    # Rivers
    Name_NC_Rivers = DC.Create_NC_name('Rivers', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Rivers):

        # Get the data of Reference Evapotranspiration and save as nc
        Rivers_CR = RC.Open_nc_array(Name_NC_Rivers_CR)
        DataCube_Rivers = RC.resize_array_example(Rivers_CR, LU_data)
        DC.Save_as_NC(Name_NC_Rivers, DataCube_Rivers, 'Rivers', LU_dataset)
        del DataCube_Rivers, Rivers_CR

    # Discharge
    # Define info for the nc files
    info = ['monthly','m3', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]

    Name_NC_Routed_Discharge = DC.Create_NC_name('Routed_Discharge', Simulation, Dir_Basin, 5, info)
    if not os.path.exists(Name_NC_Routed_Discharge):

        # Get the data of Reference Evapotranspiration and save as nc
        Routed_Discharge_CR = RC.Open_nc_array(Name_NC_Discharge)
        DataCube_Routed_Discharge = RC.resize_array_example(Routed_Discharge_CR, LU_data)
        DC.Save_as_NC(Name_NC_Routed_Discharge, DataCube_Routed_Discharge, 'Routed_Discharge', LU_dataset, Startdate, Enddate, 'monthly')
        del DataCube_Routed_Discharge, Routed_Discharge_CR





    # Get raster information
    geo_out, proj, size_X, size_Y = RC.Open_array_info(Example_dataset)

    Rivers = RC.Open_nc_array(Name_NC_Rivers_CR)

    # Create ID Matrix
    y,x = np.indices((size_Y, size_X))
    ID_Matrix = np.int32(np.ravel_multi_index(np.vstack((y.ravel(),x.ravel())),(size_Y,size_X),mode='clip').reshape(x.shape)) + 1

    # Get tiff array time dimension:
    time_dimension = int(np.shape(Discharge_dict_CR3[0])[0])

    # create an empty array
    Result = np.zeros([time_dimension, size_Y, size_X])

    for river_part in range(0,len(River_dict_CR2)):
        for river_pixel in range(1,len(River_dict_CR2[river_part])):
            river_pixel_ID = River_dict_CR2[river_part][river_pixel]
            if len(np.argwhere(ID_Matrix == river_pixel_ID))>0:
                row, col = np.argwhere(ID_Matrix == river_pixel_ID)[0][:]
                Result[:,row,col] = Discharge_dict_CR3[river_part][:,river_pixel]
        print(river_part)


    Outflow = Discharge_dict_CR3[0][:,1]

    for i in range(0,time_dimension):
        output_name = r'C:/testmap/rtest_%s.tif' %i
        Result_one = Result[i, :, :]
        DC.Save_as_tiff(output_name, Result_one, geo_out, "WGS84")

    import os

    # Get environmental variable for the Home folder
    WA_env_paths = os.environ["WA_HOME"].split(';')
    Dir_Home = WA_env_paths[0]

    # Create the Basin folder
    Dir_Basin = os.path.join(Dir_Home, Basin)
    info = ['monthly','m3-month-1', ''.join([Startdate[5:7], Startdate[0:4]]) , ''.join([Enddate[5:7], Enddate[0:4]])]
    Name_Result = DC.Create_NC_name('DischargeEnd', Simulation, Dir_Basin, 5, info)
    Result[np.logical_and(Result == 0.0, Rivers == 0.0)] = np.nan

    DC.Save_as_NC(Name_Result, Result, 'DischargeEnd', Example_dataset, Startdate, Enddate, 'monthly')



    '''


    return()






















