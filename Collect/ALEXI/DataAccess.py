# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/ETmonitor

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the ETmonitor developers.

Description:
This script collects ALEXI data from the UNESCO-IHE FTP server. The data has a
monthly temporal resolution and a spatial resolution of 0.01 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2008-01-01 till 2012-12-31.

Example:
from wa.Collect import ETmonitor
ETmonitor.monthly(Dir='C:/Temp/', Startdate='2003-02-24', Enddate='2003-03-09',
                     latlim=[50,54], lonlim=[3,7])

"""
# General modules
import numpy as np
import os
import pandas as pd
from ftplib import FTP
import datetime
import math
import glob

# Water Accounting Modules
import wa.WebAccounts as WebAccounts
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, TimeStep, Waitbar):

    """
    This scripts downloads ALEXI ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one week.
    The name of the file corresponds to the first day of the week.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    TimeStep -- 'daily' or 'weekly'  (by using here monthly, an older dataset will be used)
    lonlim -- [ymin, ymax] (values must be between -60 and 70)
    latlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -60 or latlim[1] > 70:
        print 'Latitude above 70N or below 60S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0],-60)
        latlim[1] = np.min(latlim[1],70)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)

	# Check Startdate and Enddate
    if not Startdate:
        if TimeStep == 'weekly':
            Startdate = pd.Timestamp('2003-01-01')
        if TimeStep == 'daily':
            Startdate = pd.Timestamp('2005-01-01')
    if not Enddate:
        if TimeStep == 'weekly':
            Enddate = pd.Timestamp('2015-12-31')
        if TimeStep == 'daily':
            Enddate = pd.Timestamp('2016-12-31')

	# Make a panda timestamp of the date
    try:
        Enddate = pd.Timestamp(Enddate)
    except:
        Enddate = Enddate

    if TimeStep == 'weekly':

        # Define the Startdate of ALEXI
        DOY = datetime.datetime.strptime(Startdate,
                                         '%Y-%m-%d').timetuple().tm_yday
        Year = datetime.datetime.strptime(Startdate,
                                          '%Y-%m-%d').timetuple().tm_year

      	# Change the startdate so it includes an ALEXI date
        DOYstart = int(math.ceil(DOY/7.0)*7+1)
        DOYstart = str('%s-%s' %(DOYstart, Year))
        Day = datetime.datetime.strptime(DOYstart, '%j-%Y')
        Month = '%02d' % Day.month
        Day = '%02d' % Day.day
        Date = (str(Year) + '-' + str(Month) + '-' + str(Day))
        DOY = datetime.datetime.strptime(Date,
                                         '%Y-%m-%d').timetuple().tm_yday
        # The new Startdate
        Date = pd.Timestamp(Date)

        # amount of Dates weekly
        Dates = pd.date_range(Date, Enddate, freq = '7D')

        # Define directory and create it if not exists
        output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Weekly')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    if TimeStep == 'daily':

        # Define Dates
        Dates = pd.date_range(Startdate, Enddate, freq = 'D')

        # Define directory and create it if not exists
        output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI', 'Daily')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    if TimeStep == 'weekly':
        ALEXI_weekly(Date, Enddate, output_folder, latlim, lonlim, Year, Waitbar, total_amount, TimeStep)

    if TimeStep == 'daily':
        ALEXI_daily(Dates, output_folder, latlim, lonlim, Waitbar, total_amount, TimeStep)

def ALEXI_weekly(Date, Enddate, output_folder, latlim, lonlim, Year, Waitbar, total_amount, TimeStep):

    # Define the stop conditions
    Stop = Enddate.toordinal()
    End_date=0
    amount = 0
    while End_date == 0:

        # Date as printed in filename
        Datesname=Date+pd.DateOffset(days=-7)
        DirFile= os.path.join(output_folder,'ETa_ALEXI_CSFR_mm-week-1_weekly_%s.%02s.%02s.tif' %(Datesname.strftime('%Y'), Datesname.strftime('%m'), Datesname.strftime('%d')))

        # Define end filename
        filename = "ALEXI_weekly_mm_%s_%s.tif" %(Date.strftime('%j'), Date.strftime('%Y'))

		 # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, filename)

	    # Create the new date for the next download
        Datename = (str(Date.strftime('%Y')) + '-' + str(Date.strftime('%m')) + '-' + str(Date.strftime('%d')))

        # Define IDs
        yID = 3000 - np.int16(np.array([np.ceil((latlim[1]+60)*20),np.floor((latlim[0]+60)*20)]))
        xID = np.int16(np.array([np.floor((lonlim[0])*20),np.ceil((lonlim[1])*20)])+3600)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(DirFile):
            try:
                Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename, lonlim, latlim, yID, xID, TimeStep)
            except:
                print "Was not able to download file with date %s" %Date

        # Current DOY
        DOY = datetime.datetime.strptime(Datename,
                                     '%Y-%m-%d').timetuple().tm_yday

        # Define next day
        DOY_next = int(DOY + 7)
        if DOY_next >= 366:
            DOY_next = 8
            Year += 1
        DOYnext = str('%s-%s' %(DOY_next, Year))
        DayNext = datetime.datetime.strptime(DOYnext, '%j-%Y')
        Month = '%02d' % DayNext.month
        Day = '%02d' % DayNext.day
        Date = (str(Year) + '-' + str(Month) + '-' + str(Day))

        # Adjust waitbar
        if Waitbar == 1:
            import wa.Functions.Start.WaitbarConsole as WaitbarConsole
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

        # Check if this file must be downloaded
        Date = pd.Timestamp(Date)
        if Date.toordinal() > Stop:
            End_date = 1

def ALEXI_daily(Dates, output_folder, latlim, lonlim, Waitbar, total_amount, TimeStep):

    amount = 0
    for Date in Dates:

        # Date as printed in filename
        DirFile= os.path.join(output_folder,'ETa_ALEXI_CSFR_mm-day-1_daily_%d.%02d.%02d.tif' %(Date.year, Date.month, Date.day))
        DOY = Date.timetuple().tm_yday

        # Define end filename
        filename = "EDAY_CERES_%d%03d.dat.gz" %(Date.year, DOY)

		 # Temporary filename for the downloaded global file
        local_filename = os.path.join(output_folder, filename)

        # Define IDs
        yID = 3000 - np.int16(np.array([np.ceil((latlim[1]+60)*20),np.floor((latlim[0]+60)*20)]))
        xID = np.int16(np.array([np.floor((lonlim[0])*20),np.ceil((lonlim[1])*20)])+3600)

        # Download the data from FTP server if the file not exists
        if not os.path.exists(DirFile):
            try:
                Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename, lonlim, latlim, yID, xID, TimeStep)
            except:
                print "Was not able to download file with date %s" %Date

        # Adjust waitbar
        if Waitbar == 1:
            import wa.Functions.Start.WaitbarConsole as WaitbarConsole
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    os.chdir(output_folder)
    re = glob.glob("*.dat")
    for f in re:
        os.remove(os.path.join(output_folder, f))

def Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename, lonlim, latlim, yID, xID, TimeStep):
    """
    This function retrieves ALEXI data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the ALEXI developers.

    Keyword arguments:
	local_filename -- name of the temporary file which contains global ALEXI data
    DirFile -- name of the end file with the weekly ALEXI data
    filename -- name of the end file
    lonlim -- [ymin, ymax] (values must be between -60 and 70)
    latlim -- [xmin, xmax] (values must be between -180 and 180)
    """

    # Collect account and FTP information
    username, password = WebAccounts.Accounts(Type = 'FTP_WA')
    ftpserver = "ftp.wateraccounting.unesco-ihe.org"

    # Download data from FTP
    ftp=FTP(ftpserver)
    ftp.login(username,password)
    if TimeStep is "weekly":
        directory="/WaterAccounting/Data_Satellite/Evaporation/ALEXI/World/"
    if TimeStep is "daily":
        directory="/WaterAccounting/Data_Satellite/Evaporation/ALEXI/World_05182018/"
    ftp.cwd(directory)
    lf = open(local_filename, "wb")
    ftp.retrbinary("RETR " + filename, lf.write)
    lf.close()

    if TimeStep is "weekly":

        # Open global ALEXI data
        dataset = RC.Open_tiff_array(local_filename)

        # Clip extend out of world data
        data = dataset[yID[0]:yID[1],xID[0]:xID[1]]
        data[data < 0] = -9999

    if TimeStep is "daily":

        DC.Extract_Data_gz(local_filename, os.path.splitext(local_filename)[0])

        raw_data = np.fromfile(os.path.splitext(local_filename)[0], dtype="<f4")
        dataset = np.flipud(np.resize(raw_data, [3000,7200]))
        data = dataset[yID[0]:yID[1],xID[0]:xID[1]]
        data[data < 0] = -9999

    # make geotiff file
    geo = [lonlim[0],0.05,0,latlim[1],0,-0.05]
    DC.Save_as_tiff(name = DirFile, data = data, geo = geo, projection = "WGS84")
    return
