# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/CFSR
"""
# General modules
import pandas as pd
import os
import numpy as np
from netCDF4 import Dataset
import re
from joblib import Parallel, delayed

# WA+ modules
from wa.Collect.CFSR.Download_data_CFSR import Download_data
from wa.General import data_conversions as DC

def CollectData(Dir, Var, Startdate, Enddate, latlim, lonlim, cores, Version):    
    """
    This function collects daily CFSR data in geotiff format

    Keyword arguments:
    Dir -- 'C:/file/to/path/'
    Var -- 'dlwsfc','dswsfc','ulwsfc', or 'uswsfc'
    Startdate -- 'yyyy-mm-dd'
    Enddate -- 'yyyy-mm-dd'
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    cores -- The number of cores used to run the routine.
             It can be 'False' to avoid using parallel computing
		    routines.
    Version -- 1 or 2 (1 = CFSR, 2 = CFSRv2)	
    """

				
    # Creates an array of the days of which the ET is taken
    Dates = pd.date_range(Startdate,Enddate,freq = 'D') 
    
    # For collecting CFSR data				
    if Version == 1:			
        # Check the latitude and longitude and otherwise set lat or lon on greatest extent
        if latlim[0] < -89.9171038899 or latlim[1] > 89.9171038899:
            print 'Latitude above 89.917N or below 89.917S is not possible. Value set to maximum'
            latlim[0] = np.maximum(latlim[0],-89.9171038899)
            latlim[1] = np.minimum(latlim[1],89.9171038899)
        if lonlim[0] < -180 or lonlim[1] > 179.843249782:
            print 'Longitude must be between 179.84E and 179.84W. Now value is set to maximum'
            lonlim[0] = np.maximum(lonlim[0],-180)
            lonlim[1] = np.minimum(lonlim[1],179.843249782)  
												
        # Make directory for the CFSR data
        output_folder=os.path.join(Dir,'Radiation','CFSR')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  										
												
    # For collecting CFSRv2 data    
    if Version == 2:
            # Check the latitude and longitude and otherwise set lat or lon on greatest extent
        if latlim[0] < -89.9462116040955806 or latlim[1] > 89.9462116040955806:
            print 'Latitude above 89.917N or below 89.946S is not possible. Value set to maximum'
            latlim[0] = np.maximum(latlim[0],-89.9462116040955806)
            latlim[1] = np.minimum(latlim[1],89.9462116040955806)
        if lonlim[0] < -180 or lonlim[1] > 179.8977275:
            print 'Longitude must be between 179.90E and 179.90W. Now value is set to maximum'
            lonlim[0] = np.maximum(lonlim[0],-180)
            lonlim[1] = np.minimum(lonlim[1],179.8977275)  			
				
        # Make directory for the CFSRv2 data
        output_folder=os.path.join(Dir,'Radiation','CFSRv2')
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)  				
				
				
    # Pass variables to parallel function and run
    args = [output_folder, latlim, lonlim, Var, Version]
    if not cores:
        for Date in Dates:
            RetrieveData(Date, args)
        results = True
    else:
        results = Parallel(n_jobs=cores)(delayed(RetrieveData)(Date, args)
                                         for Date in Dates)	
    
    # Remove all .nc and .grb2 files
    for f in os.listdir(output_folder):
        if re.search(".nc", f):
            os.remove(os.path.join(output_folder, f))
    for f in os.listdir(output_folder):
        if re.search(".grb2", f):
            os.remove(os.path.join(output_folder, f))	
    for f in os.listdir(output_folder):
        if re.search(".grib2", f):
            os.remove(os.path.join(output_folder, f))	
				
    return results
		
def RetrieveData(Date, args):

    # unpack the arguments
    [output_folder, latlim, lonlim, Var, Version] = args

    # Name of the model      
    if Version == 1:
        version_name = 'CFSR'
    if Version == 2:
        version_name = 'CFSRv2'								
				
    # Name of the outputfile
    if Var == 'dlwsfc':
        Outputname = 'DLWR_%s_W-m2_' %version_name + str(Date.strftime('%Y')) + '.' + str(Date.strftime('%m')) + '.' + str(Date.strftime('%d')) + '.tif'
    if Var == 'dswsfc':
        Outputname = 'DSWR_%s_W-m2_' %version_name + str(Date.strftime('%Y')) + '.' + str(Date.strftime('%m')) + '.' + str(Date.strftime('%d')) + '.tif'
    if Var == 'ulwsfc':
        Outputname = 'ULWR_%s_W-m2_' %version_name + str(Date.strftime('%Y')) + '.' + str(Date.strftime('%m')) + '.' + str(Date.strftime('%d')) + '.tif'
    if Var == 'uswsfc':
        Outputname = 'USWR_%s_W-m2_' %version_name + str(Date.strftime('%Y')) + '.' + str(Date.strftime('%m')) + '.' + str(Date.strftime('%d')) + '.tif'

    # Create the total end output name        
    outputnamePath = os.path.join(output_folder, Outputname)

    # If the output name not exists than create this output								
    if not os.path.exists(outputnamePath):								

       								
        local_filename = Download_data(Date, Version, output_folder, Var)				

        # convert grb2 to netcdf (wgrib2 module is needed)    
        for i in range(0,4):
            nameNC = 'Output' + str(Date.strftime('%Y')) + str(Date.strftime('%m')) + str(Date.strftime('%d')) + '-' + str(i+1) + '.nc'
				
            # Total path of the output 				
            FileNC6hour = os.path.join(output_folder, nameNC)
				
	       # Band number of the grib data which is converted in .nc			
            band=(int(Date.strftime('%d')) - 1) * 28 + (i + 1) * 7

            # Convert the data
            DC.Convert_grb2_to_nc(local_filename, FileNC6hour, band)
     
        if Version == 1:
									
            if Date < pd.Timestamp(pd.datetime(2010, 12, 31)):
	            		   							
                # Convert the latlim and lonlim into array
                Xstart = np.floor((lonlim[0] + 180.1562497) / 0.3125)
                Xend = np.ceil((lonlim[1] + 180.1562497) / 0.3125) + 1
                Ystart = np.floor((latlim[0] + 89.9171038899) / 0.3122121663)
                Yend = np.ceil((latlim[1] + 89.9171038899) / 0.3122121663)
            
                # Create a new dataset   
                Datatot = np.zeros([576, 1152])	

            else:
                Version = 2																
												
        if Version == 2:	
					
            # Convert the latlim and lonlim into array
            Xstart = np.floor((lonlim[0] + 180.102272725) / 0.204545)
            Xend = np.ceil((lonlim[1] + 180.102272725) / 0.204545) + 1
            Ystart = np.floor((latlim[0] + 89.9462116040955806) / 0.204423)
            Yend = np.ceil((latlim[1] + 89.9462116040955806) / 0.204423)
            
            # Create a new dataset   
            Datatot = np.zeros([880, 1760])		
					
        # Open 4 times 6 hourly dataset 
        for i in range (0, 4):
            nameNC = 'Output' + str(Date.strftime('%Y')) + str(Date.strftime('%m')) + str(Date.strftime('%d')) + '-' + str(i + 1) + '.nc'
            FileNC6hour = os.path.join(output_folder, nameNC)
            f = Dataset(FileNC6hour, mode = 'r')
            Data = f.variables['Band1'][0:int(Datatot.shape[0]), 0:int(Datatot.shape[1])]
            f.close()
            data = np.array(Data)
            Datatot = Datatot + data
           
								
        # Calculate the average in W/m^2 over the day   
        DatatotDay = Datatot / 4
        DatatotDayEnd = np.zeros([int(Datatot.shape[0]), int(Datatot.shape[1])])
        DatatotDayEnd[:,0:int(Datatot.shape[0])] = DatatotDay[:, int(Datatot.shape[0]):int(Datatot.shape[1])]
        DatatotDayEnd[:,int(Datatot.shape[0]):int(Datatot.shape[1])] = DatatotDay[:, 0:int(Datatot.shape[0])]
            
        # clip the data to the extent difined by the user
        DatasetEnd = DatatotDayEnd[int(Ystart):int(Yend), int(Xstart):int(Xend)]											
											
        # save file
        if Version == 1:
	        pixel_size = 0.3125
        if Version == 2:
	        pixel_size = 0.204545   
        geo = [lonlim[0],pixel_size,0,latlim[1],0,-pixel_size]  
        DC.Save_as_tiff(data = np.flipud(DatasetEnd), name = outputnamePath, geo = geo, projection = "WGS84") 	
				
    return True
