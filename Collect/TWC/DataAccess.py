# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/TWC

Description:
This script collects Gray water footprint data from the UNESCO-IHE FTP server. The data has a
weekly temporal resolution and a spatial resolution of 0.08333333 degree. The
resulting tiff files are in the WGS84 projection.

Requirement:
The WA_FTP username and password must be filled in the WebAccounts.py.
Contact the Water Accounting Team to get access to our WA FTP server.

Developers:
This dataset is developed by the Twente Water Centre:
Mekonnen, Mesfin M., and Arjen Y. Hoekstra. 
"Global gray water footprint and water pollution levels related to anthropogenic nitrogen loads to fresh water." 
Environmental science & technology 49.21 (2015): 12860-12868.

Example:
from wa.Collect import TWC
TWC.Gray_Water_Footprint(Dir='C:/Temp/', latlim=[50,54], lonlim=[3,7])

"""
# General modules
import numpy as np
import os
from ftplib import FTP

# Water Accounting Modules
import wa.WebAccounts as WebAccounts
import wa.General.raster_conversions as RC
import wa.General.data_conversions as DC


def DownloadData(Dir, latlim, lonlim):
    """
    This scripts downloads Gray Water Footprint data from the UNESCO-IHE ftp server.
    This dataset is created by the Twente Water Centre.
    The output files display the total ET in mm for a period of one week.
    The name of the file corresponds to the first day of the week.

    Keyword arguments:
	 Dir -- 'C:/file/to/path/'
    lonlim -- [ymin, ymax] (values must be between -60 and 84)
    latlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -60 or latlim[1] > 84:
        print 'Latitude above 84N or below 60S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0],-60)
        latlim[1] = np.min(latlim[1],84)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)
																									
    # Define directory and create it if not exists
    output_folder = os.path.join(Dir, 'TWC', 'GWF')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
				      
    # Define end filename
    filename_Out = "Gray_Water_Footprint_Fraction.tif"
    
    # Temporary filename for the downloaded global file												
    End_filename = os.path.join(output_folder, filename_Out)
       
    # Download the data from FTP server if the file not exists								
    if not os.path.exists(End_filename):
        Download_GWF_from_WA_FTP(output_folder, End_filename, lonlim, latlim)

def Download_GWF_from_WA_FTP(output_folder, filename_Out, lonlim, latlim):           
    """
    This function retrieves GWF data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.

    Keyword arguments:			
    output_folder -- name of the end file with the weekly ALEXI data
    End_filename -- name of the end file
    lonlim -- [ymin, ymax] (values must be between -60 and 70)
    latlim -- [xmin, xmax] (values must be between -180 and 180)			
    """      
												
    try:  
        # Collect account and FTP information			
        username, password = WebAccounts.Accounts(Type = 'FTP_WA')
        ftpserver = "ftp.wateraccounting.unesco-ihe.org"

        # Set the file names and directories       
        filename = "Gray_Water_Footprint.tif"	
        local_filename = os.path.join(output_folder, filename)		
			
        # Download data from FTP 													
        ftp=FTP(ftpserver)
        ftp.login(username,password)
        directory="/WaterAccounting_Guest/Static_WA_Datasets/"
        ftp.cwd(directory)
        lf = open(local_filename, "wb")
        ftp.retrbinary("RETR " + filename, lf.write)
        lf.close()

        # Clip extend out of world data
        dataset, Geo_out = RC.clip_data(local_filename, latlim, lonlim)
                
        # make geotiff file     
        DC.Save_as_tiff(name = filename_Out, data = dataset, geo = Geo_out, projection = "WGS84")																
                
        # delete old tif file
        os.remove(local_filename)
                
    except:
        print "file not exists"
							
    return
