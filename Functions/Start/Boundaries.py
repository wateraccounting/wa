# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 09:22:07 2017

@author: tih
"""

import numpy as np
import shapefile
import os

def Determine(Basin=''):
    
    # Get environmental variable for the Home folder
    SEBAL_env_paths = os.environ["WA_HOME"].split(';')
    Home_folder = SEBAL_env_paths[0]
    			
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