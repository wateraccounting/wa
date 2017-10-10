# -*- coding: utf-8 -*-
"""
Created on Tue Oct 03 10:16:06 2017

@author: tih
"""

def Get_Array(nc_filename_waterpix, Var_name, Example_dataset, Startdate, Enddate):
    
    #import general modules
    import numpy as np
    import pandas as pd
    from netCDF4 import Dataset    
    import gdal
    import osr
    
    #import WA+ modules    
    import wa.General.raster_conversions as RC
    
    '''
    #input files
    Name_NC_Runoff_CR = r'F:\\Create_Sheets\\Litani\\Simulations\\Simulation_1\\Sheet_5\\Runoff_CR_Simulation1_monthly_mm_012010_122010.nc'
    Example_dataset = r"F:\Create_Sheets\Litani\HydroSHED\DIR\DIR_HydroShed_-_15s.tif"
    NC_filename = "F:\Create_Sheets\Litani\WaterPIX\Litani.nc"
    Startdate = "2010-01-01"
    Enddate = "2010-12-31"
    Var = 'SurfaceRunoff_M'
    '''
    
    # Define Dates
    Dates = pd.date_range(Startdate, Enddate, freq = "MS")
    
    # Define end and start date
    Start = '%d%02d' %(Dates[0].year,Dates[0].month)
    End = '%d%02d' %(Dates[-1].year,Dates[-1].month)
    
    # Open netcdf of WaterPIX
    fh = Dataset(nc_filename_waterpix, 'r')

    # Get time series of WaterPIX
    time = fh.variables['time_yyyymm'][:]

    # Define time steps that are needed from WaterPIX    
    time_yes = np.zeros(len(time))
    time_yes[np.logical_and(np.int_(time) >= int(Start), np.int_(time) <= int(End))] = 1           
    time_start = time_yes[1:] - time_yes[:-1]     
    time_end = time_yes[:-1] - time_yes[1:]   

    # Set the startpoint    
    if np.sum(time_start)>0:
        Start_time = np.argwhere(time_start==1) + 1
    else:
        Start_time = 0   

    # Set the endpoint            
    if np.sum(time_end)>0:                        
        End_time = np.argwhere(time_end==1) + 1
    else:
        End_time = len(Dates) + Start_time   

    # Get the wanted variable from WaterPIX                              
    data = fh.variables[Var_name][Start_time:End_time,:,:]
    
    # Fill the WaterPIX veriable
    data_filled = np.dstack(np.ma.filled(data,np.nan))
    
    # Get WaterPIX projection
    proj = fh.variables['crs'].crs_wkt
    lon = fh.variables['longitude'][:]
    lat = fh.variables['latitude'][:]
 
    # Find WaterPIX raster parameters
    col = int(len(lon))
    row = int(len(lat))
    y_diff = (lat[0] - lat[-1])/(row - 1)
    x_diff = (lon[0] - lon[-1])/(col - 1)   
    geo = tuple([lon[0]+0.5*x_diff, -x_diff, 0.0, lat[0]+0.5*y_diff, 0.0, -y_diff])

    # Find example raster parameters
    geo_out, proj, size_X, size_Y = RC.Open_array_info(Example_dataset)
    
    # Create empty raster file
    Array_End = np.zeros([int(data_filled.shape[2]), size_Y, size_X])
    
    # Loop over time and add one time period at the time to end array
    for i in range(1,int(data_filled.shape[2])):
        
        # Create Memory file containing WaterPIX data
        mem_drv = gdal.GetDriverByName('MEM')
        dest = mem_drv.Create('', int(data_filled.shape[1]), int(data_filled.shape[0]), int(data_filled.shape[2]),
                               gdal.GDT_Float32, ['COMPRESS=LZW'])
        
        dest.SetGeoTransform(geo)
        srse = osr.SpatialReference()
        srse.SetWellKnownGeogCS("WGS84")
        dest.SetProjection(srse.ExportToWkt())
        dest.GetRasterBand(1).WriteArray(data_filled[:,:,i-1])
        dest.GetRasterBand(1).SetNoDataValue(-9999)
        
        # reproject the WaterPIX raster to the example raster
        dest_out = RC.reproject_dataset_example(dest, Example_dataset)
        
        # Write the raster array to the end raster
        Array_End[i-1,:,:] = dest_out.GetRasterBand(1).ReadAsArray()
 
    # Set nan value to 0
    Array_End[np.isnan(Array_End)] = 0
     
    return(Array_End)          

       
    
    
    
    
    
    