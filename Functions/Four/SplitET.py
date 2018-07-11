# -*- coding: utf-8 -*-
"""
Authors: Bert Coerver, Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Four
"""

# import general python modules
import pandas as pd
import numpy as np
import os

def Blue_Green(Dir_Basin, nc_outname, ETref_Product, P_Product, Startdate, Enddate):
    """
    This functions split the evapotranspiration into green and blue evapotranspiration.
    Parameters
    ----------
    nc_outname : str
        Path to the .nc file containing data
    Moving_Averaging_Length: integer
        Number defines the amount of months that are taken into account

    Returns
    -------
    ET_Blue : array
              Array[time, lat, lon] contains Blue Evapotranspiration
    ET_Green : array
              Array[time, lat, lon] contains Green Evapotranspiration
    """
    import wa.General.raster_conversions as RC
    import wa.Functions.Start.Get_Dictionaries as GD


    # Input Parameters functions
    scale = 1.1

    # Open LU map for example
    LU = RC.Open_nc_array(nc_outname, "Landuse")

    # Define monthly dates
    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')

    # Get moving window period

    # Get dictionaries and keys for the moving average
    ET_Blue_Green_Classes_dict, Moving_Window_Per_Class_dict = GD.get_bluegreen_classes(version = '1.0')
    Classes = ET_Blue_Green_Classes_dict.keys()
    Moving_Averages_Values_Array = np.ones(LU.shape) * np.nan

    # Create array based on the dictionary that gives the Moving average tail for every pixel
    for Class in Classes:
        Values_Moving_Window_Class = Moving_Window_Per_Class_dict[Class]
        for Values_Class in ET_Blue_Green_Classes_dict[Class]:
            Moving_Averages_Values_Array[LU == Values_Class] = Values_Moving_Window_Class

    Additional_Months_front = int(np.nanmax(Moving_Averages_Values_Array))
    Additional_Months_tail = 0
    Start_period = Additional_Months_front
    End_period = Additional_Months_tail * -1

     ########################### Extract ETref data #################################

    if ETref_Product is 'WA_ETref':
        # Define data path
        Data_Path_ETref = os.path.join(Dir_Basin, 'ETref', 'Monthly')
    else:
        Data_Path_ETref = ETref_Product

    ETref = Complete_3D_Array(nc_outname, 'Reference_Evapotranspiration', Startdate, Enddate, Additional_Months_front, Additional_Months_tail, Data_Path_ETref)

    ######################## Extract Precipitation data ########################

    if (P_Product == "CHIRPS" or P_Product == "RFE"):
        # Define data path
        Data_Path_P = os.path.join(Dir_Basin, 'Precipitation', P_Product, 'Monthly')
    else:
        Data_Path_P = P_Product

    P = Complete_3D_Array(nc_outname, 'Precipitation', Startdate, Enddate, Additional_Months_front, Additional_Months_tail, Data_Path_P)

    ########################## Extract actET data ##############################
    ET = RC.Open_nc_array(nc_outname, "Actual_Evapotranspiration", Startdate, Enddate)

    ############ Create average ETref and P using moving window ################
    ETref_Ave = np.ones([len(Dates),int(LU.shape[0]),int(LU.shape[1])]) * np.nan
    P_Ave = np.ones([len(Dates),int(LU.shape[0]),int(LU.shape[1])]) * np.nan
    if End_period == 0:
        P_period = P[Start_period:,:,:]
        ETref_period = ETref[Start_period:,:,:]
    else:
        P_period = P[Start_period:End_period,:,:]
        ETref_period = ETref[Start_period:End_period,:,:]

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

    ##################### Calculate ET blue and green ###########################

    # Mask out the nan values(if one of the parameters is nan, then they are all nan)
    mask = np.any([np.isnan(LU)*np.ones([len(Dates),int(LU.shape[0]),int(LU.shape[1])])==1, np.isnan(ET), np.isnan(ETref[int(ETref.shape[0])-len(Dates):,:,:]), np.isnan(P[int(ETref.shape[0])-len(Dates):,:,:]), np.isnan(P_Ave), np.isnan(ETref_Ave)],axis=0)
    ETref_period[mask] = ETref_Ave[mask] = ET[mask] = P_period[mask] = P_Ave[mask] = np.nan

    phi = ETref_Ave / P_Ave

    # Calculate Budyko-index
    Budyko = scale * np.sqrt(phi*np.tanh(1/phi)*(1-np.exp(-phi)))

    # Calculate ET green
    ETgreen_DataCube = np.minimum(Budyko*P[int(ETref.shape[0])-len(Dates):,:,:],ET)

    # Calculate ET blue
    ETblue_DataCube = ET - ETgreen_DataCube

    return(np.array(ETblue_DataCube), np.array(ETgreen_DataCube))


def Calc_budyko(phi):
    """
    This functions calculate the budyko number based on the aridity index
    Parameters
    ----------
    phi : Array
              Array[time, lat, lon] containing phi

    Returns
    -------
    Budyko : array
              Array[time, lat, lon] containing Budyko number
    """

    Budyko = np.sqrt(phi * np.tanh(1/phi) * (1-np.exp(-phi)))

    return(Budyko)

def Complete_3D_Array(nc_outname, Var, Startdate, Enddate, Additional_Months_front, Additional_Months_tail, Data_Path):

    from netCDF4 import Dataset
    import wa.General.raster_conversions as RC

    # Define startdate and enddate with moving average
    Startdate_Moving_Average = pd.Timestamp(Startdate) - pd.DateOffset(months = Additional_Months_front)
    Enddate_Moving_Average = pd.Timestamp(Enddate) + pd.DateOffset(months = Additional_Months_tail)
    Startdate_Moving_Average_String = '%d-%02d-%02d' %(Startdate_Moving_Average.year, Startdate_Moving_Average.month, Startdate_Moving_Average.day)
    Enddate_Moving_Average_String = '%d-%02d-%02d' %(Enddate_Moving_Average.year, Enddate_Moving_Average.month, Enddate_Moving_Average.day)

    # Extract moving average period before
    Year_front = int(Startdate_Moving_Average.year)
    filename_front = os.path.join(os.path.dirname(nc_outname), "%d.nc" %Year_front)
    Enddate_Front = pd.Timestamp(Startdate) - pd.DateOffset(days = 1)

    # Extract inside start and enddate
    Array_main = RC.Open_nc_array(nc_outname, Var, Startdate, Enddate)

    if Additional_Months_front > 0:

        # Extract moving average period before
        if os.path.exists(filename_front):

            # Open variables in netcdf
            fh = Dataset(filename_front)
            Variables_NC = [var for var in fh.variables]
            fh.close()

            if Var in Variables_NC:
                Array_front = RC.Open_nc_array(filename_front, Var, Startdate_Moving_Average_String, Enddate_Front)
            else:
                Array_front = RC.Get3Darray_time_series_monthly(Data_Path, Startdate_Moving_Average_String, Enddate_Front, nc_outname)

        else:
            Array_front = RC.Get3Darray_time_series_monthly(Data_Path, Startdate_Moving_Average_String, Enddate_Front, nc_outname)

        # Merge dataset
        Array_main = np.vstack([Array_front,Array_main])


    if Additional_Months_tail > 0:

        # Extract moving average period after
        Year_tail = int(Enddate_Moving_Average.year)
        filename_tail = os.path.join(os.path.dirname(nc_outname), "%d.nc" %Year_tail)
        Startdate_tail = pd.Timestamp(Enddate) + pd.DateOffset(days = 1)

         # Extract moving average period after
        if os.path.exists(filename_tail):

            # Open variables in netcdf
            fh = Dataset(filename_tail)
            Variables_NC = [var for var in fh.variables]
            fh.close()

            if Var in Variables_NC:
                Array_tail = RC.Open_nc_array(filename_tail, Var, Startdate_tail, Enddate_Moving_Average_String)
            else:
                Array_tail = RC.Get3Darray_time_series_monthly(Data_Path, Startdate_tail, Enddate_Moving_Average_String, nc_outname)

        else:
            Array_tail = RC.Get3Darray_time_series_monthly(Data_Path, Startdate_tail, Enddate_Moving_Average_String, nc_outname)

        # Merge dataset
        Array_main = np.vstack([Array_main,Array_tail])

    return(Array_main)
