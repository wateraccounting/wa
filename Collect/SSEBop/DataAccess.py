# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/SSEBop

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the SSEBop developers.

Description:
This script collects SSEBop data from the UNESCO-IHE FTP server or from the web. The data has a
monthly temporal resolution and a spatial resolution of 0.01 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2003-01-01 till present.

Example:
from wa.Collect import SSEBop
SSEBop.monthly(Dir='C:/Temp/', Startdate='2003-02-24', Enddate='2003-03-09',
                     latlim=[50,54], lonlim=[3,7])

"""
# General modules
import numpy as np
import os
import pandas as pd
from ftplib import FTP
import urllib

# Water Accounting Modules
import wa.WebAccounts as WebAccounts
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC


def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, version):
    """
    This scripts downloads SSEBop ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one month.
    The name of the file corresponds to the first day of the month.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    lonlim -- [ymin, ymax] (values must be between -90 and 90)
    latlim -- [xmin, xmax] (values must be between -180 and 180)
    """

    if version == "FTP":
        # Check the latitude and longitude and otherwise set lat or lon on greatest extent
        if latlim[0] < -59.2 or latlim[1] > 80:
            print 'Latitude above 80N or below -59.2S is not possible. Value set to maximum'
            latlim[0] = np.max(latlim[0], -59.2)
            latlim[1] = np.min(latlim[1], 80)
        if lonlim[0] < -180 or lonlim[1] > 180:
            print 'Longitude must be between 180E and 180W. Now value is set to maximum'
            lonlim[0] = np.max(lonlim[0],-180)
            lonlim[1] = np.min(lonlim[1],180)

    	# Check Startdate and Enddate
        if not Startdate:
            Startdate = pd.Timestamp('2003-01-01')
        if not Enddate:
            Enddate = pd.Timestamp('2014-10-31')

    if version == "V4":
        # Check the latitude and longitude and otherwise set lat or lon on greatest extent
        if latlim[0] < -60 or latlim[1] > 80.0022588483988670:
            print 'Latitude above 80N or below -59.2S is not possible. Value set to maximum'
            latlim[0] = np.max(latlim[0], -60)
            latlim[1] = np.min(latlim[1], 80.0022588483988670)
        if lonlim[0] < -180 or lonlim[1] > 180.0002930387853439:
            print 'Longitude must be between 180E and 180W. Now value is set to maximum'
            lonlim[0] = np.max(lonlim[0],-180)
            lonlim[1] = np.min(lonlim[1],180.0002930387853439)

    	# Check Startdate and Enddate
        if not Startdate:
            Startdate = pd.Timestamp('2003-01-01')
        if not Enddate:
            import datetime
            Enddate = pd.Timestamp(datetime.datetime.now())

    # Creates dates library
    Dates = pd.date_range(Startdate, Enddate, freq = "MS")

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Define directory and create it if not exists
    output_folder = os.path.join(Dir, 'Evaporation', 'SSEBop', 'Monthly')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for Date in Dates:

        # Define year and month
        year = Date.year
        month = Date.month

        if version == "FTP":

            # Date as printed in filename
            Filename_out= os.path.join(output_folder,'ETa_SSEBop_FTP_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))

            # Define end filename
            Filename_dir = os.path.join("%s" %year, "m%s%02d.tif" %(str(year)[2:], month))
            Filename_only = "m%s%02d.tif" %(str(year)[2:], month)

        if version == "V4":

            # Date as printed in filename
            Filename_out= os.path.join(output_folder,'ETa_SSEBop_V4_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))

            # Define the downloaded zip file
            Filename_only_zip = "m%s%02d.zip" %(str(year), month)

            # The end file name after downloading and unzipping
            Filename_only = "m%s%02d_modisSSEBopETv4_actual_mm.tif" %(str(year), month)

		  # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, Filename_only)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(Filename_out):
            try:

                if version == "FTP":
                    Download_SSEBop_from_WA_FTP(local_filename, Filename_dir)
                if version == "V4":
                    Download_SSEBop_from_Web(output_folder, Filename_only_zip)

                # Clip dataset
                RC.Clip_Dataset_GDAL(local_filename, Filename_out, latlim, lonlim)
                os.remove(local_filename)

            except:
                print "Was not able to download file with date %s" %Date

        # Adjust waitbar
        if Waitbar == 1:
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    if version == "V4":
        import glob
        os.chdir(output_folder)
        zipfiles = glob.glob("*.zip")
        for zipfile in zipfiles:
            os.remove(os.path.join(output_folder, zipfile))
        xmlfiles = glob.glob("*.xml")
        for xmlfile in xmlfiles:
            os.remove(os.path.join(output_folder, xmlfile))

    return

def Download_SSEBop_from_WA_FTP(local_filename, Filename_dir):
    """
    This function retrieves SSEBop data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the SSEBop developers.

    Keyword arguments:
	 local_filename -- name of the temporary file which contains global SSEBop data
    Filename_dir -- name of the end file with the monthly SSEBop data
    """

    # Collect account and FTP information
    username, password = WebAccounts.Accounts(Type = 'FTP_WA')
    ftpserver = "ftp.wateraccounting.unesco-ihe.org"

    # Download data from FTP
    ftp=FTP(ftpserver)
    ftp.login(username,password)
    directory="/WaterAccounting/Data_Satellite/Evaporation/SSEBop/sourcefiles/"
    ftp.cwd(directory)
    lf = open(local_filename, "wb")
    ftp.retrbinary("RETR " + Filename_dir, lf.write)
    lf.close()

    return

def Download_SSEBop_from_Web(output_folder, Filename_only_zip):
    """
    This function retrieves SSEBop data for a given date from the
    https://edcintl.cr.usgs.gov server.

    Keyword arguments:
	 local_filename -- name of the temporary file which contains global SSEBop data
    Filename_dir -- name of the end directory to put in the extracted data
    """
    # Create the total url to the webpage
    total_URL = "https://edcintl.cr.usgs.gov/downloads/sciweb1/shared/fews/web/global/monthly/eta/downloads/" + str(Filename_only_zip)

    # Download the data
    urllib.urlretrieve(total_URL, os.path.join(output_folder, Filename_only_zip))

    # unzip the file
    DC.Extract_Data(os.path.join(output_folder, Filename_only_zip), output_folder)

    return

