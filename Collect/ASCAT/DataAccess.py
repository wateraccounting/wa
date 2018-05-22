# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2018
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/ASCAT

Description:
This script collects ASCAT data from the VITO server. The data has a
daily temporal resolution and a spatial resolution of 0.25 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2007-01-01 till present.

Example:
from wa.Collect import ASCAT
ASCAT.daily(Dir='C:/Temp/', Startdate='2007-02-24', Enddate='2007-03-09',
                     latlim=[50,54], lonlim=[3,7])

"""
# General modules
import numpy as np
import os
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import h5py
import shutil

# Water Accounting Modules
import wa.WebAccounts as WebAccounts
import wa.General.data_conversions as DC


def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar):
    """
    This scripts downloads ASCAT SWI data from the VITO server.
    The output files display the Surface Water Index.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    lonlim -- [ymin, ymax]
    latlim -- [xmin, xmax]
    """

    # Check the latitude and longitude and otherwise reset lat and lon.
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below 90S is not possible.\
            Value set to maximum'
        latlim[0] = np.max(latlim[0], -90)
        latlim[1] = np.min(latlim[1], 90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W.\
            Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0], -180)
        lonlim[1] = np.min(lonlim[1], 180)

    # Check Startdate and Enddate
    if not Startdate:
        Startdate = pd.Timestamp('2007-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('2018-12-31')

    # Make a panda timestamp of the date
    try:
        Enddate = pd.Timestamp(Enddate)
    except:
        Enddate = Enddate

    # amount of Dates weekly
    Dates = pd.date_range(Startdate, Enddate, freq='D')

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix='Progress:',
                                    suffix='Complete', length=50)

    # Define directory and create it if not exists
    output_folder = os.path.join(Dir, 'SWI', 'ASCAT', 'Daily')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_folder_temp = os.path.join(Dir, 'SWI', 'ASCAT', 'Daily', 'Temp')
    if not os.path.exists(output_folder_temp):
        os.makedirs(output_folder_temp)

    # loop over dates
    for Date in Dates:

        # Define end filename
        End_filename = os.path.join(output_folder,
                                    'SWI_ASCAT_V3_Percentage_daily_%d.%02d.%02d.tif'
                                    % (Date.year, Date.month, Date.day))

        # Define IDs
        xID = 1800 + np.int16(np.array([np.ceil((lonlim[0])*10),
                                       np.floor((lonlim[1])*10)]))

        yID = np.int16(np.array([np.floor((-latlim[1])*10),
                                 np.ceil((-latlim[0])*10)])) + 900

        # Download the data from FTP server if the file not exists
        if not os.path.exists(End_filename):
            try:
                data = Download_ASCAT_from_VITO(End_filename,
                                                output_folder_temp, Date,
                                                yID, xID)
                # make geotiff file
                geo = [lonlim[0], 0.1, 0, latlim[1], 0, -0.1]
                DC.Save_as_tiff(name=End_filename, data=data,
                                geo=geo, projection="WGS84")
            except:
                print "Was not able to download file with date %s" % Date

        # Adjust waitbar
        if Waitbar == 1:
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount,
                                        prefix='Progress:', suffix='Complete',
                                        length=50)

    # remove the temporary folder
    shutil.rmtree(output_folder_temp)


def Download_ASCAT_from_VITO(End_filename, output_folder_temp, Date, yID, xID):
    """
    This function retrieves ALEXI data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the ALEXI developers.

    Keyword arguments:

    """

    # Define date
    year_data = Date.year
    month_data = Date.month
    day_data = Date.day

    # filename of ASCAT data on server
    ASCAT_date = "%d%02d%02d0000" % (year_data, month_data, day_data)
    ASCAT_name = 'SWI_%s_GLOBE_ASCAT_V3.0' % ASCAT_date
    ASCAT_filename = "g2_BIOPAR_SWI_%s_GLOBE_ASCAT_V3.0.1.zip" % ASCAT_date

    # Collect account and FTP information
    username, password = WebAccounts.Accounts(Type='VITO')
    URL = "https://land.copernicus.vgt.vito.be/PDF/datapool/Vegetation/Soil_Water/SWI_V3/%s/%s/%s/%s/%s" % (year_data, month_data, day_data,
                                          ASCAT_name, ASCAT_filename)

    # Output zipfile
    output_zipfile_ASCAT = os.path.join(output_folder_temp, ASCAT_filename)

    # Download the ASCAT data
    try:
        y = requests.get(URL, auth=HTTPBasicAuth(username, password))
    except:
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        y = requests.get(URL, auth=(username, password), verify=False)

    # Write the file in system
    z = open(output_zipfile_ASCAT, 'wb')
    z.write(y.content)
    z.close()

    # Extract the zipfile
    DC.Extract_Data(output_zipfile_ASCAT, output_folder_temp)

    # Open the file
    f = h5py.File(output_zipfile_ASCAT.replace('.zip', '.h5'))

    # Open global ASCAT data
    dataset = np.array((f['SWI']['SWI_010']).value)

    # Clip extend out of world data
    data = dataset[yID[0]:yID[1], xID[0]:xID[1]].astype("float") * 0.5
    data[data > 100] = -9999

    return(data)
