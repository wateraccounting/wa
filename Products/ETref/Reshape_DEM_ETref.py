# -*- coding: utf-8 -*-
"""
Authors: Tim Hessels and Gonzalo Espinoza
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
"""

# import general python modules
import gdal
import os
import osr

def Reshape_DEM(Dir, pixel_size, DEM_out):
    '''
	This function reshapes the DEM file if the pixel_size is defined by the user
	If this is not defined this function will be skipped
	
	Dir -- 'C:/' directory
	pixel_size -- pixel size of the ETref output
	DEM_out -- 'C:/' output filename of the reshaped DEM map
    '''	
				
	# Open the DEM map			
    g=gdal.Open(os.path.join(Dir,'HydroSHED','DEM','DEM_HydroShed_m.tif'))
    raster = g.GetRasterBand(1).ReadAsArray()
				
	# Calculate the new amount of rows and columns 			
    col=int(raster.shape[0]/(pixel_size / 0.000833333333333333315)) + 1
    row=int(raster.shape[1]/(pixel_size / 0.000833333333333333315)) + 1
     
    # Create the georeferance file					
    geo_t = g.GetGeoTransform()
    geo=list(geo_t)
    geo[1]=pixel_size 
    geo[5]=-pixel_size
    geo_new=tuple(geo)
				
	# reproject the DEM map within the memory			
    driver = gdal.GetDriverByName('MEM')
    dest = driver.Create('', row, col, 1, gdal.GDT_Float32)
    dest.SetGeoTransform(geo_new)
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS("WGS84")
    dest.SetProjection(srs.ExportToWkt())
    res = gdal.ReprojectImage(g, dest, srs.ExportToWkt(), srs.ExportToWkt())
     
	# open the reprojected dataset				
    data=dest.GetRasterBand(1).ReadAsArray()
       
	# save the reprojected dataset as geotiff						
    geo=dest.GetGeoTransform()
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(DEM_out, int(data.shape[1]), int(data.shape[0]), 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
    srs = osr.SpatialReference()
    dst_ds.SetProjection(srs.ExportToWkt())
    dst_ds.GetRasterBand(1).SetNoDataValue(-9999)
    dst_ds.SetGeoTransform(geo_new)
    dst_ds.GetRasterBand(1).WriteArray(data)
    dst_ds = None  

    return(DEM_out)
				
				