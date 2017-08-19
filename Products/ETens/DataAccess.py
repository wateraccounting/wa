# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETens
"""

# General modules
from netCDF4 import Dataset
import numpy as np
import os
import pandas as pd
import re
import pycurl
import shutil

# WA+ modules
import wa.WebAccounts as WebAccounts
from wa.General import data_conversions as DC

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar):

    # Create an array with the dates that will be calculated
    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')

   # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)

    # Define the minimum and maximum lat and long ETensemble Tile
    Min_lat_tile = int(np.floor((100 - latlim[1])/10))
    Max_lat_tile = int(np.floor((100 - latlim[0]-0.00125)/10))
    Min_lon_tile = int(np.floor((190 + lonlim[0])/10))
    Max_lon_tile = int(np.floor((190 + lonlim[1]-0.00125)/10))

    # Create the Lat and Lon tiles that will be downloaded
    Lat_tiles = [Min_lat_tile, Max_lat_tile]
    Lon_tiles = [Min_lon_tile, Max_lon_tile]

    # Define output folder and create this if it not exists
    output_folder = os.path.join(Dir, 'Evaporation', 'ETensV1_0')
    if not os.path.exists(output_folder):
       os.makedirs(output_folder)

    # Create Geotransform of the output files
    GEO_1 = lonlim[0]
    GEO_2 = 0.0025
    GEO_3 = 0.0
    GEO_4 = latlim[1]
    GEO_5 = 0.0
    GEO_6 = -0.0025
    geo = [GEO_1, GEO_2, GEO_3, GEO_4, GEO_5, GEO_6]
    geo_new=tuple(geo)

    # Define the parameter for downloading the data
    Downloaded = 0

    # Calculate the ET data date by date
    for Date in Dates:

        # Define the output name and folder
        file_name = 'ET_ETensemble250m_mm-month-1_monthly_%d.%02d.01.tif' %(Date.year,Date.month)
        output_file = os.path.join(output_folder, file_name)    

        # If output file not exists create this 
        if not os.path.exists(output_file):				

            # If not downloaded than download				
            if Downloaded == 0:

                # Download the ETens data from the FTP server													 
                Download_ETens_from_WA_FTP(output_folder, Lat_tiles, Lon_tiles)
 
                # Unzip the folder
                Unzip_ETens_data(output_folder, Lat_tiles, Lon_tiles)
                Downloaded = 1

            # Create the ET data for the area of interest 
            ET_data = Collect_dataset(output_folder, Date, Lat_tiles, Lon_tiles, latlim, lonlim)

            # Save this array as a tiff file
            DC.Save_as_tiff(output_file, ET_data, geo_new, projection='WGS84')

        # Create Waitbar
        if Waitbar == 1:
            amount += 1
            WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
    '''
    # Remove all the raw dataset    
    for v_tile in range(Lat_tiles[0], Lat_tiles[1]+1):
        for h_tile in range(Lon_tiles[0], Lon_tiles[1]+1):	
            Tilename = "h%sv%s" %(h_tile, v_tile)  
            filename = os.path.join(output_folder, Tilename)
            if os.path.exists(filename):						
                shutil.rmtree(filename)
    
    # Remove all .zip files
    for f in os.listdir(output_folder):
        if re.search(".zip", f):
            os.remove(os.path.join(output_folder, f))
    '''			
    return()			


def Download_ETens_from_WA_FTP(output_folder, Lat_tiles, Lon_tiles):           
    """
    This function retrieves ETensV1.0 data for a given date from the
    ftp.wateraccounting.unesco-ihe.org server.
				
    Restrictions:
    The data and this python file may not be distributed to others without
    permission of the WA+ team.

    Keyword arguments:
    output_folder -- Directory of the outputs
    Lat_tiles -- [Lat_min, Lat_max] Tile number of the max and min latitude tile number
    Lon_tiles -- [Lon_min, Lon_max] Tile number of the max and min longitude tile number				
    """      
    for v_tile in range(Lat_tiles[0], Lat_tiles[1]+1):
        for h_tile in range(Lon_tiles[0], Lon_tiles[1]+1):													

            Tilename = "h%sv%s.zip" %(h_tile, v_tile)
            if not os.path.exists(os.path.join(output_folder,Tilename)): 
                try:  
                    # Collect account and FTP information			
                    username, password = WebAccounts.Accounts(Type = 'FTP_WA')
                    FTP_name = "ftp://ftp.wateraccounting.unesco-ihe.org//WaterAccounting_Guest/ETensV1.1/%s" % Tilename
                    local_filename = os.path.join(output_folder, Tilename)   
			
                    # Download data from FTP 	
                    curl = pycurl.Curl()
                    curl.setopt(pycurl.URL, FTP_name)	
                    curl.setopt(pycurl.USERPWD, '%s:%s' %(username, password))								
                    fp = open(local_filename, "wb")								 
                    curl.setopt(pycurl.WRITEDATA, fp)
                    curl.perform()
                    curl.close()
                    fp.close()	
																
                except:
                    print "tile %s is not found and will be replaced by NaN values"	% Tilename
																
    return()									
																
																
def Unzip_ETens_data(output_folder, Lat_tiles, Lon_tiles):
    """
    This function extract the zip files

    Keyword Arguments:
    output_folder -- Directory of the outputs
    Lat_tiles -- [Lat_min, Lat_max] Tile number of the max and min latitude tile number
    Lon_tiles -- [Lon_min, Lon_max] Tile number of the max and min longitude tile number		
    """
    # Unzip the zip files one by one
    try:				
        for v_tile in range(Lat_tiles[0], Lat_tiles[1]+1):
            for h_tile in range(Lon_tiles[0], Lon_tiles[1]+1):													

                # Define the file and path to the zip file
                Tilename = "h%sv%s.zip" %(h_tile, v_tile)    
                input_zip_folder = os.path.join(output_folder, Tilename)				

                if os.path.exists(input_zip_folder):				 	
                    # Extract data                     
                    DC.Extract_Data(input_zip_folder, output_folder)
    except:
        print 'Was not able to unzip %s, data will be replaced by NaN values' %Tilename				
    return()	

def Collect_dataset(output_folder, Date, Lat_tiles, Lon_tiles, latlim, lonlim):												
    """
    This function creates an array for the extent

    Keyword Arguments:
    output_folder -- Directory of the outputs
	Date -- pandas timestamp			
    Lat_tiles -- [Lat_min, Lat_max] Tile number of the max and min latitude tile number
    Lon_tiles -- [Lon_min, Lon_max] Tile number of the max and min longitude tile number
    latlim -- [ymin, ymax] (values must be between -90 and 90)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)				
    """
    # The year and month of the data
    year = Date.year 
    month = Date.month  				

    # Create an empty start array
    Tot_dataset = np.zeros([4000 * (Lat_tiles[1]-Lat_tiles[0] + 1), 4000 * (Lon_tiles[1]-Lon_tiles[0] + 1)])
    
    # Open the tiles and fill in the empty array
    for v_tile in range(Lat_tiles[0], Lat_tiles[1]+1):
        for h_tile in range(Lon_tiles[0], Lon_tiles[1]+1):													

            Tilename = "h%sv%s" %(h_tile, v_tile)    
            filename = os.path.join(output_folder, Tilename,"ETensemble250m-%s-mm-Monthly-%s.nc" %(Tilename, year))
												
            if os.path.exists(filename):
                fh = Dataset(filename, mode='r')
                temporary = fh.variables['ETensemble'][:]         			             
                ETensembleMonth = temporary[month-1,:,:]
                del temporary
                fh.close()
                Tot_dataset[(v_tile - Lat_tiles[0]) * 4000 : (v_tile - Lat_tiles[0]) * 4000 + 4000,(h_tile - Lon_tiles[0]) * 4000 : (h_tile - Lon_tiles[0]) * 4000 + 4000 ] = ETensembleMonth 

            else:
                Tot_dataset[(v_tile - Lat_tiles[0]) * 4000 : (v_tile - Lat_tiles[0]) * 4000 + 4000, (h_tile - Lon_tiles[0]) * 4000 : (h_tile - Lon_tiles[0]) * 4000 + 4000 ] = np.ones([4000,4000]) * -9999												

    # Define the area of interest
    IDy_min = int(np.round(((100 - Lat_tiles[0] * 10) - latlim[1])/0.0025))
    IDy_max = int(int(Tot_dataset.shape[0]) - np.round((latlim[0] - (90 - Lat_tiles[1] * 10))/0.0025))
    IDx_min = int(np.round((lonlim[0]-(-190 + Lon_tiles[0] * 10))/0.0025))
    IDx_max = int(int(Tot_dataset.shape[1]) - np.round(((- 180 + Lon_tiles[1] * 10) - lonlim[1])/0.0025))				

    # Clip the ET data to the area of interest
    ET_data = np.zeros([int(np.round((latlim[1]-latlim[0]))/0.0025),int(np.round((lonlim[1]-lonlim[0])/0.0025))])				
    ET_data = Tot_dataset[IDy_min : IDy_max, IDx_min : IDx_max]
    ET_data[ET_data >= 9999] = np.nan			
    ET_data[ET_data <= -9999] = np.nan	
				
    return(ET_data)

