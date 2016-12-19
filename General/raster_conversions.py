# -*- coding: utf-8 -*-
"""
Created on Fri Dec 16 19:04:22 2016

@author: tih
"""
import gdal
import osr
import os
import numpy as np

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
				
				
				
				
				
