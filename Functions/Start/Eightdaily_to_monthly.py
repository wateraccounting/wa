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

def Nearest_Interpolate(Dir_Basin, Data_Path, Startdate, Enddate):
    """
    This functions calculates monthly tiff files based on the 8 daily tiff files. (will calculate the average)

    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Data_Path : str
        Path from the Dir_Basin to the 8 daily data
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 

    """  
    # import WA+ modules
    import wa.General.data_conversions as DC
    import wa.General.raster_conversions as RC
    
    # Define output folder 
    output_folder = os.path.join(Dir_Basin, Data_Path)
    
    # Change working directory
    os.chdir(output_folder)
    
    # Find all eight daily files
    files = glob.glob('*8-daily*.tif')

    # Create array with filename and keys (DOY and year) of all the 8 daily files
    i = 0
    DOY_Year = np.zeros([len(files),3])
    for File in files:

        # Get the time characteristics from the filename
        year = File.split('.')[-4][-4:]
        month = File.split('.')[-3]       
        day = File.split('.')[-2]    
        
        # Create pandas Timestamp
        date_file = '%s-%02s-%02s' %(year, month, day)
        Datum = pd.Timestamp(date_file)
        
        # Get day of year
        DOY = Datum.strftime('%j')
        
        # Save data in array
        DOY_Year[i,0] = i
        DOY_Year[i,1] = DOY
        DOY_Year[i,2] = year      
                
        # Loop over files        
        i += 1        
    
    # Define end and start date        
    Dates = pd.date_range(Startdate, Enddate, freq='MS')       
    DatesEnd = pd.date_range(Startdate, Enddate, freq='M')    

    # Get array information and define projection
    geo_out, proj, size_X, size_Y = RC.Open_array_info(files[0])
    if int(proj.split('"')[-2]) == 4326:
        proj = "WGS84" 
    
    # Get the No Data Value
    dest = gdal.Open(files[0])
    NDV = dest.GetRasterBand(1).GetNoDataValue()

    # Loop over months and create monthly tiff files
    i = 0
    for date in Dates:
        # Get Start and end DOY of the current month
        DOY_month_start = date.strftime('%j')  
        DOY_month_end = DatesEnd[i].strftime('%j')

        # Search for the files that are between those DOYs 
        year = date.year
        DOYs = DOY_Year[DOY_Year[:,2] == year]
        DOYs_oneMonth = DOYs[np.logical_and((DOYs[:,1] + 8) >= int(DOY_month_start), DOYs[:,1] <= int(DOY_month_end))]

        # Create empty arrays
        Monthly = np.zeros([size_Y, size_X])
        Weight_tot = np.zeros([size_Y, size_X])
        Data_one_month = np.ones([size_Y, size_X]) * np.nan
        
        # Loop over the files that are within the DOYs
        for EightDays in DOYs_oneMonth[:,0]:
            
            # Calculate the amount of days in this month of each file
            Weight = np.ones([size_Y, size_X])      
            
            # For start of month
            if EightDays == DOYs_oneMonth[:,0][0]:
                Weight =  Weight * int(DOYs_oneMonth[:,1][0] + 8 - int(DOY_month_start))
             
            # For end of month    
            elif EightDays == DOYs_oneMonth[:,0][-1]:    
                Weight = Weight * (int(DOY_month_end) - DOYs_oneMonth[:,1][-1] + 1)
             
            # For the middle of the month    
            else:
                Weight = Weight * 8
           
            # Open the array of current file
            input_name = os.path.join(output_folder,files[int(EightDays)])
            Data = RC.Open_tiff_array(input_name) 
                                
            # Remove NDV                          
            Weight[Data == NDV] = 0
            Data[Data == NDV] = np.nan
             
            # Multiply weight time data    
            Data = Data * Weight
              
            # Calculate the total weight and data                         
            Weight_tot += Weight         
            Monthly += Data
         
        # Go to next month    
        i += 1    
        
        # Calculate the average
        Data_one_month[Weight_tot != 0.] = Monthly[Weight_tot != 0.] / Weight_tot[Weight_tot != 0.]

        # Define output name
        output_name = os.path.join(output_folder,files[int(EightDays)].replace('8-daily', 'monthly'))
        output_name = output_name[:-6] + '01.tif'
        
        # Save tiff file
        DC.Save_as_tiff(output_name, Data_one_month, geo_out, proj)      
        
    return









        