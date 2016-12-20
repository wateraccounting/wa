# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 19:04:22 2016

@author: tih
"""
import gdal
import osr
import os
import numpy as np
from pyproj import Proj, transform

def Open_array_info(filename=''):

    f = gdal.Open(filename)
    if f is None:
        print '%s does not exists' %filename
    else:					
        geo_out = f.GetGeoTransform()
        proj = f.GetProjection()
        size_X = f.RasterXSize
        size_Y = f.RasterYSize
        f = None
    return(geo_out, proj, size_X, size_Y)		
				
def Open_tiff_array(filename='', band=''):	

    f = gdal.Open(filename)
    if f is None:
        print '%s does not exists' %filename
    else:
        if band is '':
            band = 1
        Data = f.GetRasterBand(band).ReadAsArray()				
    return(Data)

def clip_data(input_file, latlim, lonlim):
    """
    Clip the data to the defined extend of the user (latlim, lonlim) or to the
    extend of the DEM tile

    Keyword Arguments:
    input_file -- output data, output of the clipped dataset
    latlim -- [ymin, ymax]
    lonlim -- [xmin, xmax]
    """
				
    if input_file.split('.')[-1] == 'tif':
        dest_in = gdal.Open(input_file)               					
    else:
        dest_in = input_file
	
    # Open Array
    data_in = dest_in.GetRasterBand(1).ReadAsArray()	

    # Define the array that must remain
    Geo_in = dest_in.GetGeoTransform()
    Geo_in = list(Geo_in)			
    Start_x = np.max([int(round(((lonlim[0] - Geo_in[2]) - Geo_in[0])/ Geo_in[1])),0])   				
    End_x = np.min([int(round(((lonlim[1] + Geo_in[2]) - Geo_in[0])/ Geo_in[1])),int(dest_in.RasterXSize)])				
				
    Start_y = np.max([int(round((Geo_in[3] - (latlim[1] - Geo_in[5]))/ -Geo_in[5])),0])
    End_y = np.min([int(round(((latlim[0] + Geo_in[5]) - Geo_in[3])/ Geo_in[5])), int(dest_in.RasterYSize)])	

    #Create new GeoTransform
    Geo_in[0] = Geo_in[0] + Start_x * Geo_in[1]
    Geo_in[3] = Geo_in[3] + Start_y * Geo_in[5]
    Geo_out = tuple(Geo_in)
				
    data = np.zeros([End_y - Start_y, End_x - Start_x])				

    data = data_in[Start_y:End_y,Start_x:End_x] 

    return(data, Geo_out)
				
				
def reproject_dataset_epsg(dataset, pixel_spacing, epsg_to, method = 2):
    """
    A sample function to reproject and resample a GDAL dataset from within
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure is slightly long-winded, but
    goes like this:

    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """

    # 1) Open the dataset
    g = gdal.Open(dataset)
    if g is None:
        print 'input folder does not exist'

    # Get EPSG code
    epsg_from = Get_epsg(g)
   
    # Get the Geotransform vector:
    geo_t = g.GetGeoTransform()
    # Vector components:
    # 0- The Upper Left easting coordinate (i.e., horizontal)
    # 1- The E-W pixel spacing
    # 2- The rotation (0 degrees if image is "North Up")
    # 3- The Upper left northing coordinate (i.e., vertical)
    # 4- The rotation (0 degrees)
    # 5- The N-S pixel spacing, negative as it is counted from the UL corner
    x_size = g.RasterXSize  # Raster xsize
    y_size = g.RasterYSize  # Raster ysize

    epsg_to = int(epsg_to)

    # 2) Define the UK OSNG, see <http://spatialreference.org/ref/epsg/27700/>
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    inProj = Proj(init='epsg:%d' %epsg_from)
    outProj = Proj(init='epsg:%d' %epsg_to)
				
    # Up to here, all  the projection have been defined, as well as a
    # transformation from the from to the to
    ulx, uly = transform(inProj,outProj,geo_t[0], geo_t[3])
    lrx, lry = transform(inProj,outProj,geo_t[0] + geo_t[1] * x_size,
                                        geo_t[3] + geo_t[5] * y_size)

    # See how using 27700 and WGS84 introduces a z-value!
    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName('MEM')

    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    col = int((lrx - ulx)/pixel_spacing)
    rows = int((uly - lry)/pixel_spacing)

    # Re-define lr coordinates based on whole number or rows and columns
    (ulx, uly) = (int(ulx), int(uly))
    (lrx, lry) = (int(ulx) + col * pixel_spacing, int(uly) -
                  rows * pixel_spacing)
																		
    dest = mem_drv.Create('', col, rows, 1, gdal.GDT_Float32)
    if dest is None:
        print 'input folder to large for memory, clip input map'
     
   # Calculate the new geotransform
    new_geo = (int(ulx), pixel_spacing, geo_t[2], int(uly),
               geo_t[4], - pixel_spacing)
    
    # Set the geotransform
    dest.SetGeoTransform(new_geo)
    dest.SetProjection(osng.ExportToWkt())
      
    # Perform the projection/resampling
    if method is 1:				
        res = gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(),gdal.GRA_NearestNeighbour)
    if method is 2:				
        res = gdal.ReprojectImage(g, dest, wgs84.ExportToWkt(), osng.ExportToWkt(),gdal.GRA_Bilinear)						

    return dest, ulx, lry, lrx, uly, epsg_to

def reproject_dataset_example(dataset, dataset_example,method=1):

    # open dataset that must be transformed    
    g = gdal.Open(dataset)
    epsg_from = Get_epsg(g)	   

    # open dataset that is used for transforming the dataset
    gland=gdal.Open(dataset_example) 
    epsg_to = Get_epsg(gland)	

    # Set the EPSG codes
    osng = osr.SpatialReference()
    osng.ImportFromEPSG(epsg_to)
    wgs84 = osr.SpatialReference()
    wgs84.ImportFromEPSG(epsg_from)

    # Get shape and geo transform from example				
    geo_land = gland.GetGeoTransform()			
    col=gland.RasterXSize
    rows=gland.RasterYSize

    # Create new raster			
    mem_drv = gdal.GetDriverByName('MEM')
    dest1 = mem_drv.Create('', col, rows, 1, gdal.GDT_Float32)
    dest1.SetGeoTransform(geo_land)
    dest1.SetProjection(osng.ExportToWkt())
    
    # Perform the projection/resampling
    if method is 1:				
        res = gdal.ReprojectImage(g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_NearestNeighbour)
    if method is 2:				
        res = gdal.ReprojectImage(g, dest1, wgs84.ExportToWkt(), osng.ExportToWkt(), gdal.GRA_Bilinear)
    return(dest1)				
				
def Get_epsg(g):				
			
    try:
        # Get info of the dataset that is used for transforming     
        gland_proj = g.GetProjection()
        Projection=gland_proj.split('EPSG","')
        epsg_to=int((str(Projection[-1]).split(']')[0])[0:-1])				      
    except:
       epsg_to=4326	
       print 'Was not able to get the projection, so WGS84 is assumed'							
    return(epsg_to)							