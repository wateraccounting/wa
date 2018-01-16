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
    This functions calculates monthly tiff files based on the 16 daily tiff files. (will calculate the average)

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
    
    # Find all eight daily files
    files = glob.glob('*16-daily*.tif')

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
    
    # Check enddate:
    Enddate_split = Enddate.split('-')    
    month_range = calendar.monthrange(int(Enddate_split[0]),int(Enddate_split[1]))[1]
    Enddate = '%d-%02d-%02d' %(int(Enddate_split[0]),int(Enddate_split[1]),month_range)
    
    # Check startdate:
    Startdate_split = Startdate.split('-')    
    Startdate = '%d-%02d-01' %(int(Startdate_split[0]),int(Startdate_split[1]))
    
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
        DOYs_oneMonth = DOYs[np.logical_and((DOYs[:,1] + 16) >= int(DOY_month_start), DOYs[:,1] <= int(DOY_month_end))]

        # Create empty arrays
        Monthly = np.zeros([size_Y, size_X])
        Weight_tot = np.zeros([size_Y, size_X])
        Data_one_month = np.ones([size_Y, size_X]) * np.nan
        
        # Loop over the files that are within the DOYs
        for EightDays in DOYs_oneMonth[:,1]:
            
            # Calculate the amount of days in this month of each file
            Weight = np.ones([size_Y, size_X])      
            
            # For start of month
            if np.min(DOYs_oneMonth[:,1]) == EightDays:
                Weight =  Weight * int(EightDays + 16 - int(DOY_month_start))
             
            # For end of month    
            elif np.max(DOYs_oneMonth[:,1]) == EightDays:   
                Weight = Weight * (int(DOY_month_end) - EightDays + 1)
             
            # For the middle of the month    
            else:
                Weight = Weight * 16
 
            row = DOYs_oneMonth[np.argwhere(DOYs_oneMonth[:,1]==EightDays)[0][0],:][0]
         
            # Open the array of current file
            input_name = os.path.join(Dir_in, files[int(row)])
            Data = RC.Open_tiff_array(input_name) 
                                
            # Remove NDV                          
            Weight[Data == NDV] = 0
            Data[Data == NDV] = np.nan
             
            # Multiply weight time data (per day)   
            Data = Data * Weight
              
            # Calculate the total weight and data                         
            Weight_tot += Weight         
            Monthly[~np.isnan(Data)] += Data[~np.isnan(Data)]
         
        # Go to next month    
        i += 1    
        
        # Calculate the average
        Data_one_month[Weight_tot != 0.] = Monthly[Weight_tot != 0.] / Weight_tot[Weight_tot != 0.]

        # Define output directory
        if Dir_out == None:
            Dir_out = Dir_in

        # Define output name
        output_name = os.path.join(Dir_out, files[int(row)].replace('16-daily', 'monthly'))
        output_name = output_name[:-9] + '%02d.01.tif' %(date.month)
        
        # Save tiff file
        DC.Save_as_tiff(output_name, Data_one_month, geo_out, proj)      
        
    return









        