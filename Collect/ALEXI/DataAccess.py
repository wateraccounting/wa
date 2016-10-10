# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/ALEXI


Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the ALEXI developers.

Description:
This script collects ALEXI data from the UNESCO-IHE FTP server. The data has a
weekly temporal resolution and a spatial resolution of 0.05 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2003-01-01 till 2015-12-31.

The output file with the name 2003.01.01 contains the total evaporation in mm
for the period of 1 January - 7 January.

Example:
from wa.Collect import ALEXI
ALEXI.weekly(Dir='C:/Temp/', Startdate='2003-02-24', Enddate='2003-03-09',
                     latlim=[50,54], lonlim=[3,7])

"""
# General modules
import numpy as np
import os
from osgeo import osr, gdal
import pandas as pd
from ftplib import FTP
import datetime
import math

# Water Accounting Modules
import WebAccounts

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim):
    """
    This scripts downloads ALEXI ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one week.
    The name of the file corresponds to the first day of the week.

    Keyword arguments:
	Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
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
        Startdate = pd.Timestamp('2003-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('2015-12-31')
    
	# Make a panda timestamp of the date			
    try:				
        Enddate = pd.Timestamp(Enddate)
    except:
        Enddate = Enddate
	
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
																																					
    # Define directory and create it if not exists
    output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Define the stop conditions							
    Stop = Enddate.toordinal()
    End_date=0
				
    while End_date == 0:
            
        # Date as printed in filename
        Datesname=Date+pd.DateOffset(days=-7)
        DirFile=output_folder + 'ETa_ALEXI_CSFR_mm-week-1_weekly_' + Datesname.strftime('%Y') + '.' + Datesname.strftime('%m') + '.' + Datesname.strftime('%d') + '.tif'
            
        # Define end filename
        filename="ALEXI_weekly_mm_" + Date.strftime('%j') + "_"+  Date.strftime('%Y') +".tif"
        
		# Temporary filename for the downloaded global file												
        local_filename = os.path.join(output_folder, filename)
           
        # Define IDs
        yID = 3000 - np.int16(np.array([np.ceil((latlim[1]+60)*20),np.floor((latlim[0]+60)*20)]))
        xID = np.int16(np.array([np.floor((lonlim[0])*20),np.ceil((lonlim[1])*20)])+3600) 

        # Download the data from FTP server if the file not exists								
        if not os.path.exists(DirFile):
            Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename, lonlim, latlim, yID, xID)
        
		# Create the new date for the next download					
        Date = (str(Date.strftime('%Y')) + '-' + str(Date.strftime('%m')) + '-' + str(Date.strftime('%d')))						
        
		# DOY of the previous file						
        DOY = datetime.datetime.strptime(Date,'%Y-%m-%d').timetuple().tm_yday
        
		# DOY of the new file						
        DOY = DOY + 7
        if DOY == 372:
            DOY = 8
            Year = Year + 1												
        
        DOY = str(DOY)
		
        # Date of new file					
        Day = datetime.datetime.strptime(DOY, '%j')
        Month = '%02d' % Day.month
        Day = '%02d' % Day.day
        Date = (str(Year) + '-' + str(Month) + '-' + str(Day))											
        Date = pd.Timestamp(Date)

        # Check if this file must be downloaded										
        if Date.toordinal() > Stop:
            End_date = 1								


def Download_ALEXI_from_WA_FTP(local_filename, DirFile, filename, lonlim, latlim, yID, xID):           
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
												
    try:  
        
        # Collect account and FTP information			
        username, password = WebAccounts.Accounts(Type = 'FTP_WA')
        ftpserver = "ftp.wateraccounting.unesco-ihe.org"
						
        # Download data from FTP 													
        ftp=FTP(ftpserver)
        ftp.login(username,password)
        directory="/WaterAccounting/Data_Satellite/Evaporation/ALEXI/World/"
        ftp.cwd(directory)
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + filename, lf.write)
        lf.close()

        # Open global ALEXI data                
        f=gdal.Open(local_filename)
        band=f.GetRasterBand(1)
        dataset=band.ReadAsArray()
                
        # Clip extend out of world data
        data = dataset[yID[0]:yID[1],xID[0]:xID[1]]                 
        data[data < 0] = -9999
                
        # make geotiff file              
        driver = gdal.GetDriverByName("GTiff")
        dst_ds = driver.Create(DirFile, data.shape[1], int(yID[1]-yID[0]), 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS("WGS84")
        dst_ds.SetProjection(srs.ExportToWkt())
        dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
        dst_ds.SetGeoTransform([lonlim[0],0.05,0,latlim[1],0,-0.05])
        dst_ds.GetRasterBand(1).WriteArray(data)
        dst_ds = None
                
        # delete old tif file
        f=None
        os.remove(local_filename)
                
    except:
        print "file not exists"
							
    return
