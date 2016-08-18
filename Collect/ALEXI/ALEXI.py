# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Level1/ALEXI


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
from wa.Level1 import ALEXI
ALEXI.fromFTP_weekly(Startdate='2003-02-24', Enddate='2003-03-09',
                     latlim=[50,54], lonlim=[3,7], Dir='C:/Temp/')

"""

import numpy as np
import os
from osgeo import osr, gdal
import pandas as pd
from ftplib import FTP
import datetime
import math

import WebAccounts

def DownloadData(Startdate, Enddate, latlim, lonlim, Dir):
    """
    This scripts downloads ALEXI ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one week.
    The name of the file corresponds to the first day of the week.

    Keyword arguments:
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    Dir -- 'C:/file/to/path/'
    """
    username, password = WebAccounts.Accounts(Type = 'FTP_WA')

    ftpserver = "ftp.wateraccounting.unesco-ihe.org"

    DOY = datetime.datetime.strptime(Startdate,
                                     '%Y-%m-%d').timetuple().tm_yday
    Year = datetime.datetime.strptime(Startdate,
                                      '%Y-%m-%d').timetuple().tm_year
    DOYstart = int(math.ceil(DOY/7.0)*7+1)
    DOYstart = str(DOYstart)
    Day = datetime.datetime.strptime(DOYstart, '%j')
    Month = '%02d' % Day.month
    Day = '%02d' % Day.day
    Startdate = (str(Year) + '-' + str(Month) + '-' + str(Day))

    # make directory
    output_folder = os.path.join(Dir, 'Evaporation', 'ALEXI/')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if not Startdate:
        Startdate = pd.Timestamp('2003-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('Now')

    Startdate=pd.Timestamp(Startdate) +pd.DateOffset(days=7)
    StartdateRange=Startdate-pd.DateOffset(days=364)
    Enddate=pd.Timestamp(Enddate)  
    Startdate2=pd.date_range(StartdateRange,Enddate,freq = 'AS')+pd.DateOffset(days=7)
    Enddate2=pd.date_range(Startdate,Enddate,freq = 'A')
    Count=len(Enddate2)
    os.chdir(output_folder)
    i=0
    for StartdateTot in Startdate2:
        if Count is 0:
            EnddateTotaal=Enddate
        else:
            EnddateTotaal=Enddate2[i]
        StartdateTotaal=pd.Timestamp(StartdateTot)
        if i is 0:
            StartdateTotaal=Startdate
        if i==Count-1:
            EnddateTotaal=Enddate
        
        Dates = pd.date_range(StartdateTotaal,EnddateTotaal,freq = '7D')
        
        i=i+1   
        for Date in Dates:
            
            Datesname=Date+pd.DateOffset(days=-7)
            # File name .Tiff (final result)
            DirFile=output_folder + 'ETa_ALEXI_CSFR_mm-week-1_weekly_' + Datesname.strftime('%Y') + '.' + Datesname.strftime('%m') + '.' + Datesname.strftime('%d') + '.tif'
             
            ftp=FTP(ftpserver)
            ftp.login(username,password)
            directory="/WaterAccounting/Data_Satellite/Evaporation/ALEXI/World/"
            ftp.cwd(directory)
            
            filename="ALEXI_weekly_mm_" + Date.strftime('%j') + "_"+  Date.strftime('%Y') +".tif"
            
              # Define IDs
            yID = 3000 - np.int16(np.array([np.ceil((latlim[1]+60)*20),np.floor((latlim[0]+60)*20)]))
            xID = np.int16(np.array([np.floor((lonlim[0])*20),np.ceil((lonlim[1])*20)])+3600) 
                        
            try:  
                local_filename = os.path.join(output_folder, filename)
                lf = open(local_filename, "wb")
                ftp.retrbinary("RETR " + filename, lf.write)
                lf.close()
                
                f=gdal.Open(local_filename)
                band=f.GetRasterBand(1)
                dataset=band.ReadAsArray()
                
                # Clip extend out of world data
                #dataset=np.transpose(dataset)
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
                continue
