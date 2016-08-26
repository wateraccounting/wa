# -*- coding: utf-8 -*-
'''
Authors: Tim Hessels
         UNESCO-IHE 2016
Contact: t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
'''

# import general python modules
import os 
import gdal
import osr
import numpy as np

def ReprojectRaster(Source, Example, overwrite = True, output = None, method = 'average', nc_layername = None):
    """
    This function reprojects a raster by using lanczos, average, or bilinear interpolation.
    !!! need GDAL 1.11.1 version !!!
				
				
    Keyword arguments:
    Source -- 'C:/'  path to the source data (dataset that must be reprojected)
    Example -- 'C:/'  path to the example data (dataset that shows the geo-information)
    overwrite -- if the overwrite function is used than the Source path will be replaced
    output -- 'C:/' path for the reprojected output file		
    method --'average', 'lanczos', 'bilinear' defines the method for interpolation	
    nc_layername -- if the input file is an .nc file you can specify the bandname here 			
    """
	
	# look at the extension of the source data
    extension = os.path.splitext(Source)[1]
				
	# if it is a .nc file the layername will be added			
    if extension == '.nc':
        assert nc_layername != None, 'Specify nc-layername'
        src_filename = 'NETCDF:"'+Source+'":'+nc_layername
    else:
        src_filename = Source
								
    # Opens the dataset
    src = gdal.Open(src_filename, gdal.GA_ReadOnly)
    src_proj = src.GetProjection()
    NDV = src.GetRasterBand(1).GetNoDataValue()
    
    # We want a section of source that matches this:
    match_filename = Example
    match_ds = gdal.Open(match_filename, gdal.GA_ReadOnly)
    match_proj = match_ds.GetProjection()
    match_geotrans = match_ds.GetGeoTransform()
    wide = match_ds.RasterXSize
    high = match_ds.RasterYSize
    
    # Create the destination file 
    if overwrite:
        dst = gdal.GetDriverByName('GTiff').Create(Source[:-4], wide, high, 1, gdal.GDT_Float32)
    else:
        assert output != None, 'Specify output'
        dst = gdal.GetDriverByName('GTiff').Create(output, wide, high, 1, gdal.GDT_Float32)   
    dst.SetGeoTransform( match_geotrans )
    dst.SetProjection( match_proj)
    dst.GetRasterBand(1).SetNoDataValue(NDV)
    
    # apply the interpolation
    if method == 'lanczos':
        gdal.ReprojectImage(src, dst, src_proj, match_proj, gdal.GRA_Lanczos)
    if method == 'average':
        gdal.ReprojectImage(src, dst, src_proj, match_proj, gdal.GRA_Average)
    if method == 'bilinear':
        gdal.ReprojectImage(src, dst, src_proj, match_proj, gdal.GRA_Bilinear)
    
    if output == None:
        output = Source
    
    del src    
    del dst
    
    # overwrites file
    if overwrite:
        os.remove(Source)
        os.rename(Source[:-4],Source)

    return output				
				
def reproject_dataset(dataset_in, dataset_example,method):
    """
    This function reprojects a raster by using lanczos, average, or bilinear interpolation. (light function)
    !!! need GDAL 1.11.1 version !!!
				
				
    Keyword arguments:
    dataset_in -- 'C:/'  path to the source data (dataset that must be reprojected)
    dataset_example -- 'C:/'  path to the example data (dataset that shows the geo-information)
    method --'average', 'lanczos', 'bilinear' defines the method for interpolation	
    """
    # open dataset that must be transformed    
    g = gdal.Open(dataset_in)
    
    # Get the some information from the example dataset
    gdem=gdal.Open(dataset_example)
    raster_shape = OpenAsArray(dataset_example).shape 
    geo_example = gdem.GetGeoTransform()
    
    # Create new data set
    mem_drv = gdal.GetDriverByName('MEM')
    dest = mem_drv.Create('', int(raster_shape[1]), int(raster_shape[0]), 1, gdal.GDT_Float32)
    
    # Set the new geotransform
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(int(4326))
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(int(4326))
    
    # Set the geotransform
    dest.SetGeoTransform(geo_example)
    dest.SetProjection(osng.ExportToWkt())
    
    # Do the work
    if method == 'lanczos':
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Lanczos)
    if method == 'average':
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Average)
    if method == 'bilinear':
        gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear)
    return dest				
				
			
def OpenAsArray(FileName, Bandnumber = 1):
    """
    This function opens a tiff file as a numpy array
		
    Keyword arguments:
    FileName -- 'C:/'  path to the source data 
    Bandnumber -- The Bandnumber of the tiff file that must be opened	
    """

    # Open a geo-map as a numpy array
    DataSet = gdal.Open(FileName, gdal.GA_ReadOnly)
    # Get the band, default is 1.
    Band = DataSet.GetRasterBand(Bandnumber)
    # Open as an array.
    Array = Band.ReadAsArray()
    # Get the No Data Value
    NDV = Band.GetNoDataValue()
    # Convert No Data Points to nans
    Array[Array == NDV] = np.nan
    return Array    
				
def GetGeoInfo(FileName, Bandnumber = 1):
    """
    This function collect information from a tiff file
		
    Keyword arguments:
    FileName -- 'C:/'  path to the source data 
    Bandnumber -- The Bandnumber of the tiff file that must be opened	
    """

    # Function to read the original file's projection:
    SourceDS = gdal.Open(FileName, gdal.GA_ReadOnly)
    NDV = SourceDS.GetRasterBand(Bandnumber).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataType = gdal.GetDataTypeName(DataType)
    return NDV, xsize, ysize, GeoT, Projection, DataType
				
def CreateGeoTiff(Name, Array, NDV, 
                  xsize, ysize, GeoT, Projection):

    """
    This function saves a numpy array as tiff file
		
    Keyword arguments:
    Name -- 'C:/'  name of the tiff file (that will be created within the function)
    Array -- numpy array that will be saved 
    NDV -- No data value
    xsize -- x size of the numpy array
    ysize -- y size of the numpy array
    GeoT -- [ul x corner, x space, x rotation, ul y corner, y rotation, y space] Georeference information
    Projection -- the EPSG code of the output file
    """
    
    # save as a geotiff file with a resolution of 0.001 degree
    NewFileName = Name+'.tif'            
    driver = gdal.GetDriverByName("GTiff")
    dst_ds = driver.Create(NewFileName, int(Array.shape[1]), int(Array.shape[0]), 1, gdal.GDT_Float32, ['COMPRESS=LZW'])                    
    srse = osr.SpatialReference()
    srse.SetWellKnownGeogCS("WGS84")
    dst_ds.SetProjection(srse.ExportToWkt())
    Array[np.isnan(Array)]=NDV
    dst_ds.GetRasterBand(1).SetNoDataValue(NDV)
    dst_ds.SetGeoTransform(GeoT)
    dst_ds.GetRasterBand(1).WriteArray(Array)
    dst_ds = None 	