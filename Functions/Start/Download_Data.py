# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Start

Those function download the data that is not downloaded yet
"""
import os
import glob
import pandas as pd
import numpy as np
import calendar

def Precipitation(Dir, latlim, lonlim, Startdate, Enddate, Product = 'CHIRPS'):
    """
    This functions check the precipitation files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Product (optional): str
        Defines the product that will be used (default is CHIRPS)

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """

    if Product is 'CHIRPS':

        # monthly
        from wa.Collect import CHIRPS

        # Define data path
        Data_Path = os.path.join(Dir, 'Precipitation','CHIRPS', 'Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Data_Path, 'MS')

        i = 1
        # Loop over the startdates
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            CHIRPS.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'TRMM':
        from wa.Collect import TRMM

        # Define data path
        Data_Path = os.path.join(Dir, 'Precipitation','TRMM', 'Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # Download the daily data
            TRMM.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1


    elif Product is 'RFE':
        from wa.Collect import RFE

        # Define data path
        Data_Path = os.path.join(Dir, 'Precipitation','RFE', 'Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # Download the daily data
            RFE.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    else:
        Data_Path = Product

    return(Data_Path)


def Precipitation_Daily(Dir, latlim, lonlim, Startdate, Enddate, Product = 'CHIRPS'):
    """
    This functions check the precipitation files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Product (optional): str
        Defines the product that will be used (default is CHIRPS)

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """

    if Product is 'CHIRPS':

        # monthly
        from wa.Collect import CHIRPS

        # daily
        Data_Path = os.path.join(Dir, 'Precipitation','CHIRPS', 'Daily')
        Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Data_Path, 'D')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # Download the daily data
            CHIRPS.daily(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'TRMM':
        from wa.Collect import TRMM

        # daily
        Data_Path = os.path.join(Dir, 'Precipitation','TRMM', 'Daily')
        Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Data_Path, 'D')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # Download the daily data
            TRMM.daily(Dir, Startdate_Download, Enddate_download, latlim, lonlim)
            i += 1

    elif Product is 'RFE':
        from wa.Collect import RFE

        # daily
        Data_Path = os.path.join(Dir, 'Precipitation','RFE', 'Daily')
        Startdates, Enddates = Set_Start_End_Dates(Startdate,Enddate, Data_Path, 'D')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # Download the daily data
            RFE.daily(Dir, Startdate_Download, Enddate_download, latlim, lonlim)
            i += 1

    else:
        Data_Path = Product

    return(Data_Path)


def Evapotranspiration(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD16'):
    """
    This functions check the evapotranspiration files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Product (optional): str
        Defines the product that will be used (default is MOD16)

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'ETensV1_0':

        from wa.Products import ETens

        # Define data path
        Data_Path = os.path.join(Dir, 'Evaporation','ETensV1_0')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            ETens.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'MOD16':
        from wa.Collect import MOD16

        # Define data path
        Data_Path = os.path.join(Dir, 'Evaporation','MOD16','Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            MOD16.ET_monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'GLEAM':
        from wa.Collect import GLEAM

        # Define data path
        Data_Path = os.path.join(Dir, 'Evaporation','GLEAM','Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            GLEAM.ET_monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'ALEXI':

        from wa.Collect import ALEXI

        # Define data path
        Data_Path = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            ALEXI.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'ETmonitor':

        from wa.Collect import ETmonitor

        # Define data path
        Data_Path = os.path.join(Dir, 'Evaporation', 'ETmonitor', 'Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            ETmonitor.ET_monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'SSEBop':

        from wa.Collect import SSEBop

        # Define data path
        Data_Path = os.path.join(Dir, 'Evaporation', 'SSEBop', 'Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            SSEBop.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    elif Product is 'CMRSET':

        from wa.Collect import CMRSET

        # Define data path
        Data_Path = os.path.join(Dir, 'Evaporation', 'CMRSET', 'Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            CMRSET.monthly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1
    else:
        Data_Path = Product

    return(Data_Path)

def LAI(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD15'):
    """
    This functions check the Leaf Area Index files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Product (optional): str
        Defines the product that will be used (default is MOD15)

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'MOD15':
        from wa.Collect import MOD15

        # Define data path
        Data_Path = os.path.join(Dir, 'LAI','MOD15')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, '8D')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            MOD15.LAI_8daily(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1
    else:
        Data_Path = Product

    return(Data_Path)

def NPP(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD17'):
    """
    This functions check the NPP files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Product (optional): str
        Defines the product that will be used (default is MOD17)

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'MOD17':
        from wa.Collect import MOD17

        # Define data path
        Data_Path = os.path.join(Dir, 'NPP','MOD17')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'AS')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            MOD17.NPP_yearly(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1

    else:
        Data_Path = Product

    return(Data_Path)

def NDVI(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD13'):
    """
    This functions check the GPP files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Product (optional): str
        Defines the product that will be used (default is MOD17)

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'MOD13':
        from wa.Collect import MOD13

        # Define data path
        Data_Path = os.path.join(Dir, 'NDVI', 'MOD13')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, '16D')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            MOD13.NDVI_16daily(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1
    else:
        Data_Path = Product

    return(Data_Path)


def GPP(Dir, latlim, lonlim, Startdate, Enddate, Product = 'MOD17'):
    """
    This functions check the GPP files that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Product (optional): str
        Defines the product that will be used (default is MOD17)

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'MOD17':
        from wa.Collect import MOD17

        # Define data path
        Data_Path = os.path.join(Dir,'GPP','MOD17')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, '8D')

        i = 1
        for Startdate_Download in Startdates:

            # Define enddate
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            MOD17.GPP_8daily(Dir, Startdate_Download, Enddate_download,latlim, lonlim)
            i += 1
    else:
        Data_Path = Product

    return(Data_Path)

def DEM(Dir, latlim, lonlim, Resolution, Product = 'HydroSHED'):
    """
    This functions check the DEM file from SRTM that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    resolution (optional): 3s or 15s
        Defines the resolution of the product
    Product (optional): str
        Defines the product that will be used

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """

    if Product is 'HydroSHED':
        from wa.Collect import DEM

        # download data between startdate and enddate
        DEM.HydroSHED(Dir, latlim, lonlim, '%s' % Resolution)

        # Define data path
        Data_Path = os.path.join(Dir,'HydroSHED','DEM')
    else:
        Data_Path = Product

    return(Data_Path)

def DEM_Dir(Dir, latlim, lonlim, Resolution, Product = 'HydroSHED'):
    """
    This functions check the DEM direction file from SRTM that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    resolution (optional): 3s or 15s
        Defines the resolution of the product
    Product (optional): str
        Defines the product that will be used

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'HydroSHED':
        from wa.Collect import DEM

        # download data between startdate and enddate
        DEM.HydroSHED_Dir(Dir, latlim, lonlim, '%s' % Resolution)

        # Define data path
        Data_Path = os.path.join(Dir,'HydroSHED','DIR')

    else:
        Data_Path = Product

    return(Data_Path)

def JRC_occurrence(Dir, latlim, lonlim, Product):
    """
    This functions check the water occurrence file from JRC that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Product (optional): str
        Defines the product that will be used

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'JRC':
        from wa.Collect import JRC

        # download data between startdate and enddate
        JRC.Occurrence(Dir, latlim, lonlim)

        # Define data path
        Data_Path = os.path.join(Dir,'JRC','Occurrence')
    else:
        Data_Path = Product

    return(Data_Path)

def ETreference(Dir, latlim, lonlim, Startdate, Enddate, Product):
    """
    This functions check the ET reference files that needs to be downloaded, and send the request to the product functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    if Product is 'WA_ETref':

        from wa.Products import ETref

        # Define data path
        Data_Path = os.path.join(Dir,'ETref','Monthly')

        # Get start and enddates
        Startdates, Enddates = Set_Start_End_Dates(Startdate, Enddate, Data_Path, 'MS')

        i = 1
        for Startdate_Download in Startdates:
            Enddate_download = Enddates[-i]

            # download data between startdate and enddate
            ETref.monthly(Dir, Startdate_Download, Enddate_download, latlim, lonlim, pixel_size = 0.025)
            i += 1
    else:
        Data_Path = Product

    return(Data_Path)

def Soil_Properties(Dir, latlim, lonlim, Para = 'ThetaSat_TopSoil'):
    """
    This functions collect the soil properties layers from HiHydroSoil from the FTP server, by sending the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]
    Para : str
        Soil property layer that must be downloaded

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    from wa.Collect import HiHydroSoil

    if Para == 'ThetaSat_TopSoil':
        # download data between startdate and enddate
        HiHydroSoil.ThetaSat_TopSoil(Dir, latlim, lonlim)

        # Define data path
        Data_Path = os.path.join(Dir,'HiHydroSoil','ThetaSat')

    return(Data_Path)

def GWF(Dir, latlim, lonlim):
    """
    This functions check the Gray Water Footprint file from TWC that needs to be downloaded, and send the request to the collect functions.

    Parameters
    ----------
    Dir : str
        Path to all the output data of the Basin
    latlim : array
        Array containing the latitude limits [latmin, latmax]
    lonlim : array
        Array containing the longitude limits [lonmin, lonmax]

    Returns
    -------
    Data_Path : str
        Path from the Dir to the downloaded data

    """
    from wa.Collect import TWC

    # download data between startdate and enddate
    TWC.Gray_Water_Footprint(Dir, latlim, lonlim)

    # Define data path
    Data_Path = os.path.join(Dir,'TWC','GWF')

    return(Data_Path)


def Set_Start_End_Dates(Startdate, Enddate, Data_Path, freq):
    """
    This functions check all the files if they are already downloaded, or needs
    to be downloaded.

    Parameters
    ----------
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd'
    Data_Path : str
        Path to the downloaded data
    freq : 'D','8D','MS', or 'AS'
        Defines the frequenct of the dataset that must be downloaded

    Returns
    -------
    Startdates : str
        Contains all the start dates of data that needs to be downloaded
    Enddates : str
        Contains all the end dates of data that needs to be downloaded
    """

    # Check if folder already exists
    if os.path.exists(Data_Path):
        os.chdir(Data_Path)

        # Defines the dates of the 8 daily periods
        if freq == '8D':
            import wa.Collect.MOD15.DataAccess as TimeStamps_8D
            Dates = TimeStamps_8D.Make_TimeStamps(Startdate, Enddate)
        elif freq == '16D':
            import wa.Collect.MOD13.DataAccess as TimeStamps_16D
            Dates = TimeStamps_16D.Make_TimeStamps(Startdate, Enddate)
        else:
            Dates = pd.date_range(Startdate, Enddate, freq=freq)

        # Check if the dates already exists
        Date_Check = np.zeros([len(Dates) + 2])
        Date_Check_end = np.zeros([len(Dates), 2])
        i = 0

        # Loop over the dates
        for Date in Dates:
            i += 1

            # Define month, day, and year
            month = Date.month
            year = Date.year
            day = Date.day

            # Get all the files that already exists in folder
            if freq == 'MS':
                files = glob.glob('*monthly_%d.%02d.01.tif' % (year, month))
            if freq == 'AS':
                files = glob.glob('*yearly_%d.%02d.01.tif' % (year, month))
            if freq == 'D':
                files = glob.glob('*daily_%d.%02d.%02d.tif' % (year, month,
                                                               day))
            if freq == '8D':
                files = glob.glob('*8-daily_%d.%02d.%02d.tif' % (year, month,
                                                                 day))
            if freq == '16D':
                files = glob.glob('*16-daily_%d.%02d.%02d.tif' % (year, month,
                                                                 day))

            # If file exits put a 1 in the array
            if len(files) == 1:
                Date_Check[i] = 1

        # Add additional numbers to the Date_Check array
        Date_Check_end[:, 0] = Date_Check[1:-1] + Date_Check[:-2]
        Date_Check_end[:, 1] = Date_Check[1:-1] + Date_Check[2:]

        # Find place where there is a startdate
        Startdates_place = np.argwhere(np.logical_and(
            Date_Check_end[:, 0] == 1, Date_Check_end[:, 1] == 0))
        # Find place where there is a enddate
        Enddates_place = np.argwhere(np.logical_and(
            Date_Check_end[:, 1] == 1, Date_Check_end[:, 0] == 0))

        # Add all the startdates and enddates in 1 array
        if Date_Check[1] != 1:
            Startdates = [Startdate]
        else:
            Startdates = []
        if Date_Check[-2] != 1:
            Enddates = [Enddate]
        else:
            Enddates = []

        for Startdate_number in Startdates_place:
            Date = Dates[int(Startdate_number)]
            month = Date.month
            year = Date.year
            day = Date.day

            if np.any([isinstance(month, pd.core.index.Int64Index),
                       isinstance(year, pd.core.index.Int64Index),
                       isinstance(day, pd.core.index.Int64Index)]):
                month = int(Date.month[0])
                year = int(Date.year[0])
                day = int(Date.day[0])

            # Define startdate
            Startdate_one = '%d-%02d-%02d' % (year, month, day)
            Startdates = np.append(Startdates, Startdate_one)

        for Enddate_number in np.flipud(Enddates_place):
            Date = Dates[int(Enddate_number)]
            month = Date.month
            year = Date.year
            if np.any([isinstance(month, pd.core.index.Int64Index),
                       isinstance(year, pd.core.index.Int64Index)]):
                month = int(month[0])
                year = int(year[0])
            dates_in_month = calendar.monthrange(year, month)
            # Define enddate
            Enddate_one = '%d-%02d-%02d' % (year, month,
                                            int(dates_in_month[1]))
            Enddates = np.append(Enddates, Enddate_one)

    # If folder not exists than all dates must be downloaded
    else:
        Startdates = [Startdate]
        Enddates = [Enddate]

    return(Startdates, Enddates)
