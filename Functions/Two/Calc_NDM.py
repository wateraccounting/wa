# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels
         UNESCO-IHE 2017
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Function/Two
"""
# import general python modules
import os
import gdal
import numpy as np
import pandas as pd
import glob

def NPP_GPP_Based(Dir_Basin, Data_Path_GPP, Data_Path_NPP, Startdate, Enddate):
    """
    This functions calculated monthly NDM based on the yearly NPP and monthly GPP.

    Parameters
    ----------
    Dir_Basin : str
        Path to all the output data of the Basin
    Data_Path_GPP : str
        Path from the Dir_Basin to the GPP data
    Data_Path_NPP : str
        Path from the Dir_Basin to the NPP data
    Startdate : str
        Contains the start date of the model 'yyyy-mm-dd'    
    Enddate : str
        Contains the end date of the model 'yyyy-mm-dd' 
    Simulation : int
        Defines the simulation    
        
    Returns
    -------
    Data_Path_NDM : str
        Path from the Dir_Basin to the normalized dry matter data

    """ 
    # import WA+ modules
    import wa.General.data_conversions as DC
    import wa.General.raster_conversions as RC
    
    # Define output folder for Normalized Dry Matter
    Data_Path_NDM = "NDM"
    out_folder = os.path.join(Dir_Basin, Data_Path_NDM)
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)
     
    # Define input folders    
    GPP_folder = os.path.join(Dir_Basin, Data_Path_GPP)  
    NPP_folder = os.path.join(Dir_Basin, Data_Path_NPP)    

    # Define monthly time steps that will be created
    Dates = pd.date_range(Startdate, Enddate, freq = 'MS')  
    
    # Define the years that will be calculated
    Year_Start = int(Startdate[0:4])
    Year_End = int(Enddate[0:4]) 
    Years = range(Year_Start, Year_End+1) 
    
    # Loop over the years
    for year in Years:
    
        # Change working directory to the NPP folder
        os.chdir(NPP_folder)
        
        # Open yearly NPP data
        yearly_NPP_File = glob.glob('*yearly*%d.01.01.tif' %int(year))[0]
        Yearly_NPP = RC.Open_tiff_array(yearly_NPP_File)

        # Get the No Data Value of the NPP file
        dest = gdal.Open(yearly_NPP_File)
        NDV = dest.GetRasterBand(1).GetNoDataValue()        
        
        # Set the No Data Value to Nan
        Yearly_NPP[Yearly_NPP == NDV] = np.nan
        
        # Change working directory to the GPP folder
        os.chdir(GPP_folder) 
        
        # Find all the monthly files of that year
        monthly_GPP_Files = glob.glob('*monthly*%d.*.01.tif' %int(year))
        
        # Check if it are 12 files otherwise something is wrong and send the ERROR
        if not len(monthly_GPP_Files) == 12:
            print 'ERROR: Some monthly GPP Files are missing' 
        
        # Get the projection information of the GPP inputs
        geo_out, proj, size_X, size_Y = RC.Open_array_info(monthly_GPP_Files[0])
        if int(proj.split('"')[-2]) == 4326:
            proj = "WGS84" 
        
        # Get the No Data Value of the GPP files        
        dest = gdal.Open(monthly_GPP_Files[0])
        NDV = dest.GetRasterBand(1).GetNoDataValue()
        
        # Create a empty numpy array
        Yearly_GPP = np.zeros([size_Y, size_X]) 
        
        # Calculte the total yearly GPP
        for monthly_GPP_File in monthly_GPP_Files:
 
            # Open array
            Data = RC.Open_tiff_array(monthly_GPP_File)  
            
            # Remove nan values
            Data[Data == NDV] = np.nan
              
            # Add data to yearly sum    
            Yearly_GPP += Data    
            
        # Loop over the monthly dates   
        for Date in Dates:
            
            # If the Date is in the same year as the yearly NPP and GPP
            if Date.year == year:
                
                # Create empty GPP array
                monthly_GPP = np.ones([size_Y, size_X]) * np.nan
                
                # Get current month
                month = Date.month
                
                # Get the GPP file of the current year and month
                monthly_GPP_File = glob.glob('*monthly_%d.%02d.01.tif' %(int(year), int(month)))[0]
                monthly_GPP = RC.Open_tiff_array(monthly_GPP_File) 
                monthly_GPP[monthly_GPP == NDV] = np.nan
                
                # Calculate the NDM based on the monthly and yearly NPP and GPP (fraction of GPP)
                Monthly_NDM = Yearly_NPP * monthly_GPP / Yearly_GPP * (30./12.) *10000 # kg/ha
                
                # Define output name                                                      
                output_name = os.path.join(out_folder, 'NDM_MOD17_kg_ha-1_monthly_%d.%02d.01.tif' %(int(year), int(month))) 
                 
                # Save the NDM as tiff file                                                     
                DC.Save_as_tiff(output_name, Monthly_NDM, geo_out, proj)

    return(Data_Path_NDM)                                                      
                
                
                