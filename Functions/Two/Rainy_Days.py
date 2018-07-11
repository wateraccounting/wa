# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Two
"""
# Import general modules
import calendar
import glob
import os
import pandas as pd
import numpy as np

def Calc_Rainy_Days(Dir_Basin, Data_Path_P, Startdate, Enddate):
    """
    This functions calculates the amount of rainy days based on daily precipitation data.

    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Data_Path_P : str
        Path to the daily rainfall data
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'

    Returns
    -------
    Data_Path_RD : str
        Path from the Dir_Basin to the rainy days data

    """
    # import WA+ modules
    import wa.General.data_conversions as DC
    import wa.General.raster_conversions as RC

    # Create an output directory to store the rainy days tiffs
    Data_Path_RD = os.path.join(Dir_Basin, 'Rainy_Days')
    if not os.path.exists(Data_Path_RD):
        os.mkdir(Data_Path_RD)

    # Define the dates that must be created
    Dates = pd.date_range(Startdate, Enddate, freq ='MS')

    # Set working directory to the rainfall folder
    os.chdir(Data_Path_P)

    # Open all the daily data and store the data in a 3D array
    for Date in Dates:
        # Define the year and month and amount of days in month
        year = Date.year
        month = Date.month
        daysinmonth = calendar.monthrange(year, month)[1]

        # Set the third (time) dimension of array starting at 0
        i = 0

        # Find all files of that month
        files = glob.glob('*daily_%d.%02d.*.tif' %(year, month))

        # Check if the amount of files corresponds with the amount of days in month
        if len(files) is not daysinmonth:
            print 'ERROR: Not all Rainfall days for month %d and year %d are downloaded'  %(month, year)

        # Loop over the days and store data in raster
        for File in files:
            dir_file = os.path.join(Data_Path_P, File)

            # Get array information and create empty numpy array for daily rainfall when looping the first file
            if File == files[0]:

                # Open geolocation info and define projection
                geo_out, proj, size_X, size_Y = RC.Open_array_info(dir_file)
                if int(proj.split('"')[-2]) == 4326:
                    proj = "WGS84"

                # Create empty array for the whole month
                P_Daily = np.zeros([daysinmonth,size_Y, size_X])

            # Open data and put the data in 3D array
            Data = RC.Open_tiff_array(dir_file)

            # Remove the weird numbers
            Data[Data<0] = 0

            # Add the precipitation to the monthly cube
            P_Daily[i, :, :] = Data
            i += 1

        # Define a rainy day
        P_Daily[P_Daily > 0.201] = 1
        P_Daily[P_Daily != 1] = 0

        # Sum the amount of rainy days
        RD_one_month = np.nansum(P_Daily,0)

        # Define output name
        Outname = os.path.join(Data_Path_RD, 'Rainy_Days_NumOfDays_monthly_%d.%02d.01.tif' %(year, month))

        # Save tiff file
        DC.Save_as_tiff(Outname, RD_one_month, geo_out, proj)

    return(Data_Path_RD)