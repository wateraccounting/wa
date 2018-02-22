# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
         g.espinoza@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/HiHydroSoil

Restrictions:
The data and this python file may not be distributed to others without
permission of the WA+ team due data restriction of the HiHydroSoil developers.

Description:
This script collects HiHydroSoil data from the UNESCO-IHE FTP server. The
resulting tiff files are in the WGS84 projection.

Example:
from wa.Collect import HiHydroSoil
HiHydroSoil.ThetaSat(Dir='C:/Temp/', latlim=[50,54], lonlim=[3,7])

"""
# General modules
import numpy as np
import os
from ftplib import FTP
import scipy.io as spio

# Water Accounting Modules
import wa.WebAccounts as WebAccounts
import wa.General.data_conversions as DC

def DownloadData(Dir, latlim, lonlim, Waitbar):
    """
    This scripts downloads HiHydroSoil Saturated Theta soil data from the UNESCO-IHE ftp server.

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    lonlim -- [ymin, ymax] (values must be between -90 and 90)
    latlim -- [xmin, xmax] (values must be between -180 and 180)
    """
    # Check the latitude and longitude and otherwise set lat or lon on greatest extent
    if latlim[0] < -90 or latlim[1] > 90:
        print 'Latitude above 90N or below -90S is not possible. Value set to maximum'
        latlim[0] = np.max(latlim[0], -90)
        latlim[1] = np.min(latlim[1], 90)
    if lonlim[0] < -180 or lonlim[1] > 180:
        print 'Longitude must be between 180E and 180W. Now value is set to maximum'
        lonlim[0] = np.max(lonlim[0],-180)
        lonlim[1] = np.min(lonlim[1],180)
      
    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        amount = 0
        WaitbarConsole.printWaitBar(amount, 1, prefix = 'Progress:', suffix = 'Complete', length = 50)																																		
																																					
    # Define directory and create it if not exists
    output_folder = os.path.join(Dir, 'HiHydroSoil', 'ThetaSat')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
	
    # Date as printed in filename
    Filename_out= os.path.join(output_folder,'Theta_Saturated_Topsoil_HiHydroSoil.tif')
    
    # Define end filename
    Filename_in = os.path.join("wcsat_topsoil.tif")
    
		 # Temporary filename for the downloaded global file												
    local_filename = os.path.join(output_folder, Filename_in)
 
    # Download the data from FTP server if the file not exists								
    if not os.path.exists(Filename_out):
        try:
            Download_HiHydroSoil_from_WA_FTP(local_filename, Filename_in)
          
            # Clip dataset
            Clip_Dataset(local_filename, Filename_out, latlim, lonlim)
            os.remove(local_filename)
            
        except:
            print "Was not able to download file" 
 
    # Adjust waitbar
    if Waitbar == 1:
        amount += 1
        WaitbarConsole.printWaitBar(amount, 1, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return					

def Download_HiHydroSoil_from_WA_FTP(local_filename, Filename_in):           
    """
    This function retrieves HiHydroSoil data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.
				
    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team due data restriction of the HiHydroSoil developers.

    Keyword arguments:
	 local_filename -- name of the temporary file which contains global HiHydroSoil data			
    Filename_in -- name of the end file with the HiHydroSoil data
    """      
												
    # Collect account and FTP information			
    username, password = WebAccounts.Accounts(Type = 'FTP_WA')
    ftpserver = "ftp.wateraccounting.unesco-ihe.org"
						
    # Download data from FTP 													
    ftp=FTP(ftpserver)
    ftp.login(username,password)
    directory="/WaterAccounting_Guest/Static_WA_Datasets/"
    ftp.cwd(directory)
    lf = open(local_filename, "wb")
    ftp.retrbinary("RETR " + Filename_in, lf.write)
    lf.close()
      							
    return

def Clip_Dataset(local_filename, Filename_out, latlim, lonlim):
    
    import wa.General.raster_conversions as RC
    
    # Open Dataset
    HiHydroSoil_Array = RC.Open_tiff_array(local_filename)

    # Define area
    XID = [int(np.floor((180 + lonlim[0])/0.00833333)), int(np.ceil((180 + lonlim[1])/0.00833333))]
    YID = [int(np.ceil((90 - latlim[1])/0.00833333)), int(np.floor((90 -  latlim[0])/0.00833333))]

    # Define Georeference
    geo = tuple([-180 + 0.00833333*XID[0],0.00833333,0,90 - 0.00833333*YID[0],0,-0.00833333])

    # Clip Array
    HiHydroSoil_Array_clipped = HiHydroSoil_Array[YID[0]:YID[1], XID[0]:XID[1]]

    # Save tiff file
    DC.Save_as_tiff(Filename_out, HiHydroSoil_Array_clipped, geo, "WGS84")
