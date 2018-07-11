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
    from netCDF4 import Dataset

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

    # Get the boundaries of the basin based on the shapefile of the watershed
    # Boundaries, Shape_file_name_shp = Start.Boundaries.Determine(Basin)
    Boundaries, Example_dataset = Start.Boundaries.Determine_LU_Based(Basin, Dir_Home)

    ############## Cut dates into pieces if it is needed ######################

    # Check the years that needs to be calculated
    years = range(int(Startdate.split('-')[0]),int(Enddate.split('-')[0]) + 1)

    for year in years:

        # Create Start and End date for time chunk
        Startdate_part = '%d-01-01' %int(year)
        Enddate_part = '%s-12-31' %int(year)

        # Create Directory
        Dir_Basin = os.path.join(Dir_Home, Basin)
        output_dir = os.path.join(Dir_Basin, "Simulations", "Simulation_%d" %Simulation)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create .nc file if not exists
        nc_outname = os.path.join(output_dir, "%d.nc" % year)
        if not os.path.exists(nc_outname):
            DC.Create_new_NC_file(nc_outname, Example_dataset, Basin)

        ############################# Download Data ###################################
        # Open variables in netcdf
        fh = Dataset(nc_outname)
        Variables_NC = [var for var in fh.variables]
        fh.close()

        if not "Precipitation" in Variables_NC:
            Data_Path_P_Monthly = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, P_Product)

        if not "Rainy_Days" in Variables_NC:
            Data_Path_P_Daily = Start.Download_Data.Precipitation_Daily(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, P_Product)

        if not "Actual_Evapotranspiration" in Variables_NC:
            Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, ET_Product)

        if not "LAI" in Variables_NC:
            Data_Path_LAI = Start.Download_Data.LAI(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, LAI_Product)

        if not "Normalized_Dry_Matter" in Variables_NC:
                Data_Path_NPP = Start.Download_Data.NPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, NDM_Product)
                Data_Path_GPP = Start.Download_Data.GPP(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, NDM_Product)

        ########################### Create input data #################################

        if not "Rainy_Days" in Variables_NC:

            # Create Rainy Days based on daily CHIRPS
            Data_Path_RD = Two.Rainy_Days.Calc_Rainy_Days(Dir_Basin, Data_Path_P_Daily, Startdate_part, Enddate_part)

        if not "LAI" in Variables_NC:

            # Create monthly LAI
            Start.Eightdaily_to_monthly_state.Nearest_Interpolate(Data_Path_LAI, Startdate_part, Enddate_part)

        if not "Normalized_Dry_Matter" in Variables_NC:

            # Create NDM based on MOD17
            if NDM_Product == 'MOD17':

                # Create monthly GPP
                Start.Eightdaily_to_monthly_state.Nearest_Interpolate(Data_Path_GPP, Startdate_part, Enddate_part)
                Data_Path_NDM = Two.Calc_NDM.NPP_GPP_Based(Dir_Basin, Data_Path_GPP, Data_Path_NPP, Startdate_part, Enddate_part)

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

        #_______________________________Rainy Days_________________________________

        if not "Rainy_Days" in Variables_NC:
            # Get the data of rainy days and save as nc
            DataCube_RD = RC.Get3Darray_time_series_monthly(Data_Path_RD, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_RD, "Rainy_Days", "amount_of_days", 0.01)
            del DataCube_RD

        #_______________________________Leaf Area Index____________________________

        if not "LAI" in Variables_NC:
            # Get the data of leave area index and save as nc
            DataCube_LAI = RC.Get3Darray_time_series_monthly(Data_Path_LAI, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_LAI, "LAI", "m2-m-2", 0.01)
            del DataCube_LAI


        ####################### Calculations Sheet 2 ##########################
        if not ("Interception" in Variables_NC or "Transpiration" in Variables_NC or "Evaporation" in Variables_NC):
            DataCube_I, DataCube_T, DataCube_E = Two.SplitET.ITE(Dir_Basin, nc_outname, Startdate_part, Enddate_part, Simulation)

            DC.Add_NC_Array_Variable(nc_outname, DataCube_I, "Interception", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_T, "Transpiration", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_E, "Evaporation", "mm/month", 0.01)
            del DataCube_I, DataCube_T, DataCube_E

        ######################### Create CSV 2 ################################

        Dir_Basin_CSV = Generate.CSV.Create(Dir_Basin, Simulation, Basin, Startdate_part, Enddate_part, nc_outname, Example_dataset)

    ############################ Create Sheet 2 ###############################

    Generate.PDF.Create(Dir_Basin, Basin, Simulation, Dir_Basin_CSV)

    return()



















