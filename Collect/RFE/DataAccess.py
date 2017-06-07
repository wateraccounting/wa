# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/RFE
"""

import numpy as np
import os
import pandas as pd
from ftplib import FTP
from joblib import Parallel, delayed

import wa.General.data_conversions as DC
import wa.General.raster_conversions as RC

def DownloadData(Dir, Startdate, Enddate, latlim, lonlim, Waitbar, cores):
    """
    This function downloads RFE daily or monthly data

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine. It can be 'False'
             to avoid using parallel computing routines.
    TimeCase -- String equal to 'daily' or 'monthly'
    Waitbar -- 1 (Default) will print a waitbar   
    """

	# Check variables
    if not Startdate:
        Startdate = pd.Timestamp('2001-01-01')
    if not Enddate:
        Enddate = pd.Timestamp('Now')
    Dates = pd.date_range(Startdate,  Enddate, freq='D')
    
    # Create Waitbar
    if Waitbar == 1:
        import wa.Functions.Start.WaitbarConsole as WaitbarConsole
        total_amount = len(Dates)
        amount = 0
        WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)  
    
    if latlim[0] < -40.05 or latlim[1] > 40.05:
        print ('Latitude above 50N or below 50S is not possible.'
               ' Value set to maximum')
        latlim[0] = np.max(latlim[0], -40.05)
        latlim[1] = np.min(lonlim[1], 40.05)
    if lonlim[0] < -20.05 or lonlim[1] > 55.05:
        print ('Longitude must be between 180E and 180W.'
               ' Now value is set to maximum')
        lonlim[0] = np.max(latlim[0], -20.05)
        lonlim[1] = np.min(lonlim[1], 55.05)
    
	 # Make directory
    output_folder = os.path.join(Dir, 'Precipitation', 'RFE', 'Daily/')     
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)


    # Define IDs
    yID = 801 - np.int16(np.array([np.ceil((latlim[1] + 40.05)*10),
                                    np.floor((latlim[0] + 40.05)*10)-1]))
    xID = np.int16(np.array([np.floor((lonlim[0] + 20.05)*10),
                             np.ceil((lonlim[1] + 20.05)*10)+1]))

    # Pass variables to parallel function and run
    args = [output_folder, lonlim, latlim, xID, yID]
    
    if not cores:
        for Date in Dates:
            RetrieveData(Date, args)
            if Waitbar == 1:
                amount += 1
                WaitbarConsole.printWaitBar(amount, total_amount, prefix = 'Progress:', suffix = 'Complete', length = 50)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                         for Date in Dates)
        
    return results


def RetrieveData(Date, args):
    """
    This function retrieves RFE data for a given date from the
    ftp://disc2.nascom.nasa.gov server.

    Keyword arguments:
    Date -- 'yyyy-mm-dd'
    args -- A list of parameters defined in the DownloadData function.
    """
    # Argument
    [output_folder, lonlim, latlim, xID, yID] = args

    # Create https
    DirFile = os.path.join(output_folder,'P_RFE.v2.0_mm-day-1_daily_%s.%02s.%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d')))
            
    if not os.path.isfile(DirFile):
        # open ftp server
        ftp = FTP("ftp.cpc.ncep.noaa.gov", "", "")
        ftp.login()
				
    	 # Define FTP path to directory 			
        pathFTP = 'fews/fewsdata/africa/rfe2/geotiff/'

        # find the document name in this directory								
        ftp.cwd(pathFTP)
        listing = []
				
        # read all the file names in the directory			
        ftp.retrlines("LIST", listing.append)
				
    	  # create all the input name (filename) and output (outfilename, filetif, DiFileEnd) names			
        filename = 'africa_rfe.%s%02s%02s.tif.zip' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d'))
        outfilename = os.path.join(output_folder,'africa_rfe.%s%02s%02s.tif' %(Date.strftime('%Y'), Date.strftime('%m'), Date.strftime('%d'))) 
 
        try:
            local_filename = os.path.join(output_folder, filename)
            lf = open(local_filename, "wb")
            ftp.retrbinary("RETR " + filename, lf.write)
            lf.close()

            # unzip the file
            zip_filename = os.path.join(output_folder, filename)
            DC.Extract_Data(zip_filename, output_folder)

            # open tiff file
            dataset = RC.Open_tiff_array(outfilename)

            # clip dataset to the given extent
            data = dataset[yID[0]:yID[1], xID[0]:xID[1]]
            data[data < 0] = -9999

            # save dataset as geotiff file
            latlim_adj = 40.05 - 0.1 * yID[0] 
            lonlim_adj = -20.05 + 0.1 * xID[0]             
            geo = [lonlim_adj, 0.1, 0, latlim_adj, 0, -0.1]
            DC.Save_as_tiff(name=DirFile, data=data, geo=geo, projection="WGS84")

            # delete old tif file
            os.remove(outfilename)
            os.remove(zip_filename)
            
        except:
            print "file not exists"            


    return True
