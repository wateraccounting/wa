# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/TRMM
"""

import numpy as np
import os
import pandas as pd
import requests
import calendar
from joblib import Parallel, delayed

import wa.General.data_conversions as DC

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, cores, TimeCase):
    """
    This function downloads TRMM daily or monthly data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine. It can be 'False'
             to avoid using parallel computing routines.
    TimeCase -- String equal to 'daily' or 'monthly'
    Waitbar -- 1 (Default) will print a waitbar
    """
    # String Parameters
    if TimeCase == 'daily':
        TimeFreq = 'D'
        output_folder = os.path.join(Dir, 'Precipitation', 'TRMM', 'Daily')
    elif TimeCase == 'monthly':
        TimeFreq = 'MS'
        output_folder = os.path.join(Dir, 'Precipitation', 'TRMM', 'Monthly')
    else:
        raise KeyError("The input time interval is not supported")

	# Make directory
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

	# Check variables
    if not Startdate:
        Startdate = pd.Timestamp('1998-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('Now')
    Dates = pd.date_range(Startdate,  Enddate, freq=TimeFreq)

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    if latlim[0] < -50 or latlim[1] > 50:
        print ('Latitude above 50N or below 50S is not possible.'
               ' Value set to maximum')
        latlim[0] = np.max(latlim[0], -50)
        latlim[1] = np.min(lonlim[1], 50)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print ('Longitude must be between 180E and 180W.'
               ' Now value is set to maximum')
        lonlim[0] = np.max(latlim[0], -180)
        lonlim[1] = np.min(lonlim[1], 180)

    # Define IDs
    yID = np.int16(np.array([np.ceil((latlim[0] + 50)*4),
                                   np.floor((latlim[1] + 50)*4)]))
    xID = np.int16(np.array([np.floor((lonlim[0])*4),
                             np.ceil((lonlim[1])*4)]) + 720)

    # Pass variables to parallel function and run
    args = [output_folder, TimeCase, xID, yID, lonlim, latlim]

    if not cores:
        for Date in Dates:
            RetrieveData(Date, args)
            if Waitbar == 1:
                amount += 1
                WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                         for Date in Dates)

    return results


def RetrieveData(Date, args):
    """
    This function retrieves TRMM data for a given date from the
    ftp://disc2.nascom.nasa.gov server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, TimeCase, xID, yID, lonlim, latlim] = args

    year = Date.year
    month= Date.month
    day = Date.day

    from wa import WebAccounts
    username, password = WebAccounts.Accounts(Type = 'NASA')

    # Create https
    if TimeCase == 'daily':
        URL = 'https://disc2.gesdisc.eosdis.nasa.gov/opendap/TRMM_L3/TRMM_3B42_Daily.7/%d/%02d/3B42_Daily.%d%02d%02d.7.nc4.ascii?precipitation[%d:1:%d][%d:1:%d]'  %(year, month, year, month, day, xID[0], xID[1]-1, yID[0], yID[1]-1)
        DirFile = os.path.join(output_folder, "P_TRMM3B42.V7_mm-day-1_daily_%d.%02d.%02d.tif" %(year, month, day))
        Scaling = 1

    if TimeCase == 'monthly':
        if Date >= pd.Timestamp('2010-10-01'):
            URL = 'https://disc2.gesdisc.eosdis.nasa.gov/opendap/TRMM_L3/TRMM_3B43.7/%d/3B43.%d%02d01.7.HDF.ascii?precipitation[%d:1:%d][%d:1:%d]'  %(year, year, month, xID[0], xID[1]-1, yID[0], yID[1]-1)

        else:
            URL = 'https://disc2.gesdisc.eosdis.nasa.gov/opendap/TRMM_L3/TRMM_3B43.7/%d/3B43.%d%02d01.7A.HDF.ascii?precipitation[%d:1:%d][%d:1:%d]'  %(year, year, month, xID[0], xID[1]-1, yID[0], yID[1]-1)

        Scaling = calendar.monthrange(year,month)[1] * 24
        DirFile = os.path.join(output_folder, "P_TRMM3B43.V7_mm-month-1_monthly_%d.%02d.01.tif" %(year, month))

    if not os.path.isfile(DirFile):
        dataset = requests.get(URL, allow_redirects=False,stream = True)
        try:
            get_dataset = requests.get(dataset.headers['location'], auth = (username,password),stream = True)
        except:
            from requests.packages.urllib3.exceptions import InsecureRequestWarning
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            get_dataset  = requests.get(dataset.headers['location'], auth = (username, password), verify = False)

        # download data (first save as text file)
        pathtext = os.path.join(output_folder,'temp.txt')
        z = open(pathtext,'w')
        z.write(get_dataset.content)
        z.close()

        # Open text file and remove header and footer
        data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,delimiter=',')
        data = data_start[:,1:] * Scaling
        data[data < 0] = -9999
        data = data.transpose()
        data = np.flipud(data)

        # Delete .txt file
        os.remove(pathtext)

        # Make geotiff file
        geo = [lonlim[0], 0.25, 0, latlim[1], 0, -0.25]
        DC.Save_as_tiff(name=DirFile, data=data, geo=geo, projection="WGS84")

    return True
