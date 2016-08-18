"""
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Collect/CFSR
"""
# General modules
import gdal
import osr
import numpy as np

def Save_as_Gtiff(data, Version, fileName, lonlim, latlim):
    """
    This function downloads CFSR data from the FTP server
				For - CFSR:    ftp://nomads.ncdc.noaa.gov/CFSR/HP_time_series/
				    - CFSRv2:  http://nomads.ncdc.noaa.gov/modeldata/cfsv2_analysis_timeseries/

    Keyword arguments:
    data -- numpy array of the  geotiff
    Version -- 1 or 2 (1 = CFSR, 2 = CFSRv2)			
    fileName -- The directory for storing the downloaded files
    latlim -- [ymin, ymax] (values must be between -50 and 50)
    lonlim -- [xmin, xmax] (values must be between -180 and 180)
    """   
	# Define pixel_size for the geotiff			
    if Version == 1:
	    pixel_size = 0.3125
    if Version == 2:
	    pixel_size = 0.204545
	
    # Make geotiff file              
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(fileName, data.shape[1], data.shape[0], 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform([lonlim[0],pixel_size,0,latlim[1],0,-pixel_size])
    dst_ds.GetRasterBand(1).WriteArray(np.flipud(data))
    dst_ds = None   