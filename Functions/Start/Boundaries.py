# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 09:22:07 2017

@author: tih
"""

import numpy as np
import shapefile
import gdal
import os

def Determine(Basin, Home_folder):
      			
    Shape_file_name_shp = os.path.join(Home_folder,'Basins', Basin + '.shp')
    if not os.path.exists(Shape_file_name_shp):
        print '%s is missing' %Shape_file_name_shp				
    Shape_file_name_dbf = os.path.join(Home_folder,'Basins', Basin + '.dbf')
    if not os.path.exists(Shape_file_name_dbf):
        print '%s is missing' %Shape_file_name_dbf					

    Basin_shp = shapefile.Reader(Shape_file_name_shp, Shape_file_name_dbf)
    Shape = Basin_shp.shapes()
    bbox = Shape[0].bbox
    Boundaries = dict()
    #Boundaries['Lonmin'] = np.floor(bbox[0]) - 0.1
    #Boundaries['Lonmax'] = np.ceil(bbox[2]) + 0.1
    #Boundaries['Latmin'] = np.floor(bbox[1]) - 0.1
    #Boundaries['Latmax'] = np.ceil(bbox[3]) + 0.1
    Boundaries['Lonmin'] = round(np.floor((bbox[0] * 10.) - 1.))/10.
    Boundaries['Lonmax'] = round(np.ceil((bbox[2] * 10.) + 1.))/10.
    Boundaries['Latmin'] = round(np.floor((bbox[1] * 10.) - 1.))/10.
    Boundaries['Latmax'] = round((np.ceil(bbox[3] * 10.) + 1.))/10.				
    return(Boundaries, Shape_file_name_shp)

def Determine_LU_Based(Basin, Home_folder):
    

    LU_file_name = os.path.join(Home_folder,'LU', Basin + '.tif')
    if not os.path.exists(LU_file_name):
        print '%s is missing' %LU_file_name				
        
    dest = gdal.Open(LU_file_name)
    Transform = dest.GetGeoTransform()
    sizeX = dest.RasterXSize
    sizeY = dest.RasterYSize
    
    #Boundaries['Lonmin'] = np.floor(bbox[0]) - 0.1
    #Boundaries['Lonmax'] = np.ceil(bbox[2]) + 0.1
    #Boundaries['Latmin'] = np.floor(bbox[1]) - 0.1
    #Boundaries['Latmax'] = np.ceil(bbox[3]) + 0.1
    Boundaries = dict()
    Boundaries['Lonmin'] = round(np.floor((Transform[0] * 10.) - 1.))/10.
    Boundaries['Lonmax'] = round(np.ceil(((Transform[0] + sizeX * Transform[1])  * 10.) + 1.))/10.
    Boundaries['Latmin'] = round(np.floor(((Transform[3] + sizeY * Transform[5])  * 10.) - 1.))/10.
    Boundaries['Latmax'] = round((np.ceil(Transform[3] * 10.) + 1.))/10.
				
    return(Boundaries, LU_file_name)