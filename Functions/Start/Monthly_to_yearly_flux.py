# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Start
"""
# General Python modules
import numpy as np
import os
import glob
import pandas as pd
import gdal
import calendar

def Nearest_Interpolate(Dir_in, Startdate, Enddate, Dir_out = None):
    """
    This functions calculates yearly tiff files based on the monthly tiff files. (will calculate the total sum)

    Parameters
    ----------
    Dir_in : str
        Path to the input data
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Dir_out : str
        Path to the output data, default is same as Dir_in

    """  
    # import WA+ modules
    import wa.General.data_conversions as DC
    import wa.General.raster_conversions as RC
       
    # Change working directory
    os.chdir(Dir_in)
    
    # Define end and start date        
    Dates = pd.date_range(Startdate, Enddate, freq='AS')    
	
    # Find all monthly files
    files = glob.glob('*monthly*.tif')
    
    # Get array information and define projection
    geo_out, proj, size_X, size_Y = RC.Open_array_info(files[0])
    if int(proj.split('"')[-2]) == 4326:
        proj = "WGS84" 
    
    # Get the No Data Value
    dest = gdal.Open(files[0])
    NDV = dest.GetRasterBand(1).GetNoDataValue()

    for date in Dates:
        Year = date.year
        files_one_year = glob.glob('*monthly*%d*.tif' %Year)

        # Create empty arrays
        Year_data = np.zeros([size_Y, size_X])
        
        if len(files_one_year) is not int(12):
		    print("One month is missing!!!")
        
		
        for file_one_year in files_one_year:
            file_path = os.path.join(Dir_in, file_one_year)
 			
            Month_data = RC.Open_tiff_array(file_path)
            Month_data[np.isnan(Month_data)] = 0.0
            Month_data[Month_data == -9999] = 0.0
            Year_data += Month_data
		
        # Define output directory
        if Dir_out == None:
             Dir_out = Dir_in

        # Define output name
        output_name = os.path.join(Dir_out, file_one_year.replace('monthly', 'yearly').replace('month','year'))
        output_name = output_name[:-14] + '%d.01.01.tif' %(date.year)
				
        # Save tiff file
        DC.Save_as_tiff(output_name, Year_data, geo_out, proj)      
        
    return









        