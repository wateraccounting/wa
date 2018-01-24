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
This script collects ETmonitor data from the UNESCO-IHE FTP server. The data has a
monthly temporal resolution and a spatial resolution of 0.01 degree. The
resulting tiff files are in the WGS84 projection.
The data is available between 2008-01-01 till 2012-12-31.

Example:
from wa.Collect import ETmonitor
ETmonitor.ET_monthly(Dir='C:/Temp/', Startdate='2003-02-24', Enddate='2003-03-09',
                     latlim=[50,54], lonlim=[3,7])

"""
# General modules
import numpy as np
import os
import pandas as pd
from ftplib import FTP

# Water Accounting Modules
import wa.WebAccounts as WebAccounts
import wa.General.raster_conversions as RC


def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Type, Waitbar):
    """
    This scripts downloads ETmonitor ET data from the UNESCO-IHE ftp server.
    The output files display the total ET in mm for a period of one month.
    The name of the file corresponds to the first day of the month.

    Keyword arguments:
	 Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    lonlim -- [ymin, ymax] (values must be between -90 and 90)
    latlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below 90S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0], -90)
        latlim[1] = np.min(latlim[1], 90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)
								
	# Check Startdate and Enddate			
    if not Startdate:
        Startdate = pd.Timestamp('2008-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('2012-12-31')
    
    # Creates dates library
    Dates = pd.date_range(Startdate, Enddate, freq = "MS")
      
    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)																																		
																																					
    # Define directory and create it if not exists
    if Type == "act":
        output_folder = os.path.join(Dir, 'Evaporation', 'ETmonitor', 'Monthly')
    if Type == "pot":
        output_folder = os.path.join(Dir, 'ETpot', 'ETmonitor', 'Monthly')
    if Type == "ei":
        output_folder = os.path.join(Dir, 'Ei', 'ETmonitor', 'Monthly')        
    if Type == "es":
        output_folder = os.path.join(Dir, 'Es', 'ETmonitor', 'Monthly')
    if Type == "ew":
        output_folder = os.path.join(Dir, 'Ew', 'ETmonitor', 'Monthly')
    if Type == "tr":
        output_folder = os.path.join(Dir, 'Transpiration', 'ETmonitor', 'Monthly')        
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
		
    for Date in Dates:
          
        # Define year and month
        year = Date.year
        month = Date.month   

        # Define end filename and Date as printed in filename
        if Type == "act":
            Filename_in = "ET_ETmonitor_mm-month_%d_%02d_01.tif" %(year, month)
            Filename_out= os.path.join(output_folder,'ETa_ETmonitor_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))
       			
        if Type == "pot":
            Filename_in = "ETpot_ETmonitor_mm-month_%d_%02d_01.tif" %(year, month)
            Filename_out= os.path.join(output_folder,'ETpot_ETmonitor_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))

        if Type == "ei":
            Filename_in = "Ei_ETmonitor_mm-month_%d_%02d_01.tif" %(year, month)
            Filename_out= os.path.join(output_folder,'Ei_ETmonitor_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))

        if Type == "es":
            Filename_in = "Es_ETmonitor_mm-month_%d_%02d_01.tif" %(year, month)
            Filename_out= os.path.join(output_folder,'Es_ETmonitor_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))

        if Type == "ew":
            Filename_in = "Ew_ETmonitor_mm-month_%d_%02d_01.tif" %(year, month)
            Filename_out= os.path.join(output_folder,'Ew_ETmonitor_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))

        if Type == "tr":
            Filename_in = "Tr_ETmonitor_mm-month_%d_%02d_01.tif" %(year, month)
            Filename_out= os.path.join(output_folder,'Tr_ETmonitor_mm-month-1_monthly_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))
        
		  # Temporary filename for the downloaded global file												
        local_filename = os.path.join(output_folder, Filename_in)
 
        # Download the data from FTP server if the file not exists								
        if not os.path.exists(Filename_out):
            try:
                Download_ETmonitor_from_WA_FTP(local_filename, Filename_in, Type)
           
        
                # Reproject dataset
                epsg_to ='4326'
                name_reprojected_ETmonitor = RC.reproject_MODIS(local_filename, epsg_to)
        
                # Clip dataset
                RC.Clip_Dataset_GDAL(name_reprojected_ETmonitor, Filename_out, latlim, lonlim)
                os.remove(name_reprojected_ETmonitor)  
                os.remove(local_filename)  
                
            except:
                print "Was not able to download file with date %s" %Date 
 
        # Adjust waitbar
        if Waitbar == 1:
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return					

def Download_ETmonitor_from_WA_FTP(local_filename, Filename_in, Type):           
    """
    This function retrieves ETmonitor data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.
				
    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the ETmonitor developers.

    Keyword arguments:
	 local_filename -- name of the temporary file which contains global ETmonitor data			
    Filename_in -- name of the end file with the weekly ETmonitor data	
	 Type = Type of data ("act" or "pot")
    """      
												
    # Collect account and FTP information			
    username, password = WebAccounts.Accounts(Type = 'FTP_WA')
    ftpserver = "ftp.wateraccounting.unesco-ihe.org"
						
    # Download data from FTP 													
    ftp=FTP(ftpserver)
    ftp.login(username,password)
    if Type == "pot":
        directory="/WaterAccounting/Data_Satellite/Evaporation/ETmonitor/Potential_Evapotranspiration/"
    else:
        directory="/WaterAccounting/Data_Satellite/Evaporation/ETmonitor/Global/"        
    ftp.cwd(directory)
    lf = open(local_filename, "wb")
    ftp.retrbinary("RETR " + Filename_in, lf.write)
    lf.close()
      							
    return
