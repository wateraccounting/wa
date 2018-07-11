# -*- coding: utf-8 -*-

# General modules
import numpy as np
import os
import pandas as pd
import requests
from joblib import Parallel, delayed

# Water Accounting modules
from wa import WebAccounts
import wa.General.data_conversions as DC

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, cores, TimeCase):
    """
    This function downloads MSWEP Version 2.1 daily or monthly data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Var -- 'wind_f_inst' : (string) For all variable codes: VariablesInfo('day').descriptions.keys()
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Waitbar -- 0 or 1 (1 is waitbar on)
    cores -- 1....8
    """

    # Load factors / unit / type of variables / accounts
    username, password = WebAccounts.Accounts(Type = 'MSWEP')

    # Set required data for the daily option
    if TimeCase == 'daily':

        # Define output folder and create this one if not exists
        path = os.path.join(Dir, 'Precipitation', 'MSWEP', 'daily')

        if not os.path.exists(path):
            os.makedirs(path)

        # Startdate if not defined
        sd_date = '1979-01-01'

        # Define Time frequency
        TimeFreq = 'D'

        # Define URL by using personal account
        url = 'https://%s:%s@data.princetonclimate.com/opendap/MSWEP_V2.1/global_daily_010deg/' %(username,password)

        # Name the definition that will be used to obtain the data
        RetrieveData_fcn = RetrieveData_daily

    # Set required data for the monthly option
    elif TimeCase == 'monthly':

        # Define output folder and create this one if not exists
        path = os.path.join(Dir, 'Precipitation', 'MSWEP', 'monthly')

        if not os.path.exists(path):
            os.makedirs(path)

        # Startdate if not defined
        sd_date = '1979-01-01'

        # Define Time frequency
        TimeFreq = 'MS'

        # Define URL by using personal account
        url = 'https://%s:%s@data.princetonclimate.com:443/opendap/MSWEP_V2.1/global_monthly_010deg.nc' %(username,password)

        # Name the definition that will be used to obtain the data
        RetrieveData_fcn = RetrieveData_monthly

    # If none of the possible option are chosen
    else:
        raise KeyError("The input time interval is not supported")

    # Define IDs (latitude/longitude)
    yID = np.int16(np.array([np.ceil((latlim[0] + 90) * 10),
                             np.floor((latlim[1] + 90) * 10)]))
    xID = np.int16(np.array([np.floor((lonlim[0] + 180) * 10),
                             np.ceil((lonlim[1] + 180) * 10)]))

    # Check dates. If no dates are given, the max number of days is used.
    if not Startdate:
        Startdate = pd.Timestamp(sd_date)
    if not Enddate:
        Enddate = pd.Timestamp('Now')  # Should be much than available

    # Create all dates that will be calculated
    Dates = pd.date_range(Startdate, Enddate, freq=TimeFreq)

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Create one parameter with all the required arguments
    args = [path, url, TimeCase, xID, yID, lonlim, latlim, username, password]

    # Pass variables to parallel function and run
    if not cores:
        for Date in Dates:
            RetrieveData_fcn(Date, args)
            if Waitbar == 1:
                amount += 1
                WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData_fcn)(Date, args)
                                         for Date in Dates)
    return results


def RetrieveData_daily(Date, args):
    """
    This function retrieves MSWEP precipitation daily data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """

    # Open all the parameters
    [path, url, TimeCase, xID, yID, lonlim, latlim, username, password] = args

    # Reset the begin parameters for downloading
    downloaded = 0
    N = 0

    # Check whether the file already exist or
    # the worldfile is downloaded
    BasinDir = path + '/P_MSWEP_mm-day_daily_' + Date.strftime('%Y.%m.%d') + '.tif'

    # Check if the outputfile already excists
    if not os.path.isfile(BasinDir):

        # Create the time dimension
        zID_start = Date.day - 1
        month = Date.month
        year = Date.year

        # define total url
        url_MSWEP = url + '%s%02d.nc.ascii?precipitation[%s][%s:1:%s][%s:1:%s]' %(year, int(month), zID_start,yID[0],yID[1],xID[0],xID[1])

        # if not downloaded try to download file
        while downloaded == 0:
            try:

                # open URL
                try:
                    dataset = requests.get(url_MSWEP, allow_redirects=False,stream = True)
                except:
                    from requests.packages.urllib3.exceptions import InsecureRequestWarning
                    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                    dataset = requests.get(url_MSWEP, allow_redirects=False,stream = True, verify = False)

                # download data (first save as text file)
                pathtext = os.path.join(path,'temp.txt')
                z = open(pathtext,'w')
                z.write(dataset.content)
                z.close()

                # Open text file and remove header and footer
                data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,delimiter=',')
                data = data_start[1:,1:]

                # Set Nan value for values lower than -9999
                data[data < -9998] = np.nan

                # Say that download was succesfull
                downloaded = 1

            # If download was not succesfull
            except:

                data=[]

                # Try another time
                N = N + 1

                # Stop trying after 10 times
                if N == 10:
                    print 'Data from ' + Date.strftime('%Y-%m-%d') + ' is not available'
                    downloaded = 1

            # define geo
            lonlimMSWEP = xID[0] * 0.10 - 180
            latlimMSWEP  = yID[1] * 0.10 - 90

            # Save to geotiff file
            geo = [lonlimMSWEP ,0.1,0,latlimMSWEP ,0,-0.1]
            DC.Save_as_tiff(name=BasinDir, data = data, geo=geo, projection="WGS84")

            # Delete data and text file
            del data
            os.remove(pathtext)

    return True

def RetrieveData_monthly(Date, args):
    """
    This function retrieves MSWEP precipitation monthly data for a given date.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [path, url, TimeCase, xID, yID, lonlim, latlim, username, password] = args

    # Check whether the file already exist or the worldfile is downloaded
    BasinDir = path + '/P_MSWEP_mm-month_monthly_' + Date.strftime('%Y.%m.%d') + '.tif'

    # Define month and year of current month
    Y = Date.year
    M = Date.month

    # Check if the outputfile already excists
    if not os.path.isfile(BasinDir):

        # Reset the begin parameters for downloading
        downloaded = 0
        N=0

        # Create the time dimension
        zID = (Y - 1979) * 12 + (M - 1)

        # define total url
        url_MSWEP  = url + '.ascii?precipitation[%s][%s:1:%s][%s:1:%s]' %(zID,yID[0],yID[1],xID[0],xID[1])

        # if not downloaded try to download file
        while downloaded == 0:
            try:

                # open URL
                try:
                    dataset = requests.get(url_MSWEP , allow_redirects=False,stream = True)
                except:
                    from requests.packages.urllib3.exceptions import InsecureRequestWarning
                    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                    dataset = requests.get(url_MSWEP , allow_redirects=False,stream = True, verify = False)

                # download data (first save as text file)
                pathtext = os.path.join(path,'temp%s.txt' %str(zID))
                z = open(pathtext,'w')
                z.write(dataset.content)
                z.close()

                # Open text file and remove header and footer
                data_start = np.genfromtxt(pathtext,dtype = float,skip_header = 1,skip_footer = 6,delimiter=',')
                data = data_start[1:,1:]

                # Set Nan value for values lower than -9999
                data[data < -9998] = np.nan

                # Say that download was succesfull
                downloaded = 1

            # If download was not succesfull
            except:

                data=[]

                # Try another time
                N = N + 1

                # Stop trying after 10 times
                if N == 10:
                    print 'Data from ' + Date.strftime('%Y-%m-%d') + ' is not available'
                    downloaded = 1

            # define geo
            lonlimMSWEP  = xID[0] * 0.10 - 180
            latlimMSWEP  = yID[1] * 0.10 - 90

            # Save to geotiff file
            geo = [lonlimMSWEP ,0.1,0,latlimMSWEP ,0,-0.1]
            DC.Save_as_tiff(name=BasinDir, data = data, geo=geo, projection="WGS84")

            # Delete data and text file
            del data
            os.remove(pathtext)

	    return True

