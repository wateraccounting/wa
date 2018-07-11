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
import numpy as np
import pandas as pd
from netCDF4 import Dataset

def Calculate(WA_HOME_folder, Basin, P_Product, ET_Product, LAI_Product, ETref_Product, Runoff_Product, Startdate, Enddate, Simulation):
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
    LAI_Product : str
        Name of the LAI product that will be used
    Runoff_Product : str
        Name of the Runoff product that will be used
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
    import wa.Functions.Start.Get_Dictionaries as GD

    ######################### Set General Parameters ##############################

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

        ############################# Download Data ###################################

        # Download data
        if not "Precipitation" in Variables_NC:
            Data_Path_P_Monthly = Start.Download_Data.Precipitation(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, P_Product)

        if not "Actual_Evapotranspiration" in Variables_NC:
            Data_Path_ET = Start.Download_Data.Evapotranspiration(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_part, Enddate_part, ET_Product)

        if not "Reference_Evapotranspiration" in Variables_NC:
            Data_Path_ETref = Start.Download_Data.ETreference(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Startdate_Moving_Average_String, Enddate_part, ETref_Product)

        if not "Grey_Water_Footprint" in Variables_NC:
            Data_Path_GWF = Start.Download_Data.GWF(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']])

        if not "Theta_Saturated_Topsoil" in Variables_NC:
            Data_Path_ThetaSat_topsoil = Start.Download_Data.Soil_Properties(Dir_Basin, [Boundaries['Latmin'],Boundaries['Latmax']],[Boundaries['Lonmin'],Boundaries['Lonmax']], Para = 'ThetaSat_TopSoil')

        ###################### Save Data as netCDF files ##############################

        #______________________________Precipitation_______________________________

        # 1.) Precipitation data
        if not "Precipitation" in Variables_NC:
            # Get the data of Precipitation and save as nc
            DataCube_Prec = RC.Get3Darray_time_series_monthly(Data_Path_P_Monthly, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Prec, "Precipitation", "mm/month", 0.01)
            del DataCube_Prec

       #_______________________Reference Evaporation______________________________

        # 2.) Reference Evapotranspiration data
        if not "Reference_Evapotranspiration" in Variables_NC:
            # Get the data of Precipitation and save as nc
            DataCube_ETref = RC.Get3Darray_time_series_monthly(Data_Path_ETref, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ETref, "Reference_Evapotranspiration", "mm/month", 0.01)
            del DataCube_ETref

        #_______________________________Evaporation________________________________

        # 3.) Evapotranspiration data
        if not "Actual_Evapotranspiration" in Variables_NC:
            # Get the data of Evaporation and save as nc
            DataCube_ET = RC.Get3Darray_time_series_monthly(Data_Path_ET, Startdate_part, Enddate_part, Example_data = Example_dataset)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ET, "Actual_Evapotranspiration", "mm/month", 0.01)
            del DataCube_ET

        #_____________________________________GWF__________________________________

        # 4.) Grey Water Footprint data
        if not "Grey_Water_Footprint" in Variables_NC:
            # Get the data of grey water footprint and save as nc
            GWF_Filepath = os.path.join(Dir_Basin, Data_Path_GWF, "Gray_Water_Footprint_Fraction.tif")
            dest_GWF = RC.reproject_dataset_example(GWF_Filepath, Example_dataset, method=1)
            DataCube_GWF = dest_GWF.GetRasterBand(1).ReadAsArray()
            DC.Add_NC_Array_Static(nc_outname, DataCube_GWF, "Grey_Water_Footprint", "fraction", 0.0001)
            del DataCube_GWF

    ####################### Calculations Sheet 4 ##############################

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

        #____________ Evapotranspiration data split in ETblue and ETgreen ____________

        if not ("Blue_Evapotranspiration" in Variables_NC or "Green_Evapotranspiration" in Variables_NC):

            # Calculate Blue and Green ET
            DataCube_ETblue, DataCube_ETgreen = Four.SplitET.Blue_Green(Dir_Basin, nc_outname, ETref_Product, P_Product, Startdate, Enddate)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ETblue, "Blue_Evapotranspiration", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_ETgreen, "Green_Evapotranspiration", "mm/month", 0.01)
            del DataCube_ETblue, DataCube_ETgreen

        #____________ Calculate non-consumend and Total supply maps by using fractions and consumed maps (blue ET) ____________

        if not ("Total_Supply" in Variables_NC or "Non_Consumed_Water" in Variables_NC):

            # Do the calculations
            DataCube_Total_Supply, DataCube_Non_Consumed = Four.Total_Supply.Fraction_Based(nc_outname, Startdate_part, Enddate_part)

            # Save the Total Supply and non consumed data as NetCDF files
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Total_Supply, "Total_Supply", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Non_Consumed, "Non_Consumed_Water", "mm/month", 0.01)
            del DataCube_Total_Supply, DataCube_Non_Consumed

        #____________ Apply fractions over total supply to calculate gw and sw supply ____________

        if not ("Total_Supply_Surface_Water" in Variables_NC or "Total_Supply_Ground_Water" in Variables_NC):

            # Do the calculations
            DataCube_Total_Supply_SW, DataCube_Total_Supply_GW = Four.SplitGW_SW_Supply.Fraction_Based(nc_outname, Startdate_part, Enddate_part)

            # Save the Total Supply surface water and Total Supply ground water data as NetCDF files
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Total_Supply_SW, "Total_Supply_Surface_Water", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, DataCube_Total_Supply_GW, "Total_Supply_Ground_Water", "mm/month", 0.01)
            del DataCube_Total_Supply_SW, DataCube_Total_Supply_GW

        #____________ Apply gray water footprint fractions to calculated non recoverable flow based on the non consumed flow ____________


        if not ("Non_Recovable_Flow" in Variables_NC or "Recovable_Flow" in Variables_NC):

            # Calculate the non recovable flow and recovable flow by using Grey Water Footprint values
            DataCube_NonRecovableFlow, Datacube_RecovableFlow = Four.SplitNonConsumed_NonRecov.GWF_Based(nc_outname, Startdate_part, Enddate_part)

            # Get the data of Evaporation and save as nc
            DC.Add_NC_Array_Variable(nc_outname, DataCube_NonRecovableFlow, "Non_Recovable_Flow", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, Datacube_RecovableFlow, "Recovable_Flow", "mm/month", 0.01)
            del DataCube_NonRecovableFlow, Datacube_RecovableFlow

        #____________Apply fractions to calculate the non recovarable SW/GW and recovarable SW/GW ____________

        # 1. Non recovarable flow
        if not ("Non_Recovable_Flow_Ground_Water" in Variables_NC or "Non_Recovable_Flow_Surface_Water" in Variables_NC):

            # Calculate the non recovable return flow to ground and surface water
            DataCube_NonRecovableFlow_Return_GW, Datacube_NonRecovableFlow_Return_SW = Four.SplitGW_SW_Return.Fraction_Based(nc_outname, "Non_Recovable_Flow", Startdate_part, Enddate_part)

            # Get the data of Evaporation and save as nc
            DC.Add_NC_Array_Variable(nc_outname, DataCube_NonRecovableFlow_Return_GW, "Non_Recovable_Flow_Ground_Water", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, Datacube_NonRecovableFlow_Return_SW, "Non_Recovable_Flow_Surface_Water", "mm/month", 0.01)
            del DataCube_NonRecovableFlow_Return_GW, Datacube_NonRecovableFlow_Return_SW

        # 2. Recovarable flow
        if not ("Recovable_Flow_Ground_Water" in Variables_NC or "Recovable_Flow_Surface_Water" in Variables_NC):

            # Calculate the non recovable return flow to ground and surface water
            DataCube_RecovableFlow_Return_GW, Datacube_RecovableFlow_Return_SW = Four.SplitGW_SW_Return.Fraction_Based(nc_outname, "Recovable_Flow", Startdate_part, Enddate_part)

            # Get the data of Evaporation and save as nc
            DC.Add_NC_Array_Variable(nc_outname, DataCube_RecovableFlow_Return_GW, "Recovable_Flow_Ground_Water", "mm/month", 0.01)
            DC.Add_NC_Array_Variable(nc_outname, Datacube_RecovableFlow_Return_SW, "Recovable_Flow_Surface_Water", "mm/month", 0.01)
            del DataCube_RecovableFlow_Return_GW, Datacube_RecovableFlow_Return_SW

        ############################ Create CSV 4 #################################

        Dir_Basin_CSV, Unit_front = Generate.CSV.Create(Dir_Basin, Simulation, Basin, Startdate_part, Enddate_part, nc_outname)

    ############################ Create Sheet 4 ###############################

    Generate.PDF.Create(Dir_Basin, Basin, Simulation, Dir_Basin_CSV, Unit_front)

    return()






















